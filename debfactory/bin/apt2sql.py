#!/usr/bin/python
"""
  (C) Copyright 2009-2010, GetDeb Team - https://launchpad.net/~getdeb
  --------------------------------------------------------------------
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
  --------------------------------------------------------------------

  This file provides several functions to handle debian packages
  control files.


Usage:
    apt2sql.py [--database mysql://user:password@localhost/apt2sql] \
        [archive_root_url suite [component1[, component2] ]]
        
Example:
    apt2sql.py http://archive.ubuntu.com/ubuntu karmic
"""    

# sqlalchemy uses a deprecated module
import warnings
warnings.simplefilter("ignore",DeprecationWarning)

import re
import md5
from datetime import datetime
from optparse import OptionParser
from tempfile import NamedTemporaryFile
import types
import gzip
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
from localaux import *
from packages_model import *
from dpkg_control import *
from lockfile import *

# Some global variables
Log = Logger()
force_rpool = False
check_last_modified = False
check_list = None

# Get the last modified time for an URL specified file    
def get_last_mofified_time(file_url):
    """
    Returns the last modified time for the specified url
    """    
    try:
        f = urllib2.urlopen(file_url)
    except HTTPError, e:        
        Log.print_("Error %s : %s" % (e.code, file_url))
        return None    
    last_modified = f.info()['Last-Modified']        
    f.close()    
    d_last_modified = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
    return d_last_modified    
    
def import_repository(archive_url, suite, requested_components \
        , requested_architectures):
    """
    Import a repository into the dabase
    """
    global check_list
    # Get the base release file to check the list of available 
    # architectures and components
    Log.log("Importing repository: %s %s [%s] [%s]" \
        % (archive_url, suite, requested_components or "all" \
            , requested_architectures or "all"))
    release_file = "%s/dists/%s/Release" % (archive_url, suite)
    Log.log("Downloading %s" % release_file)
    try:
        remote_file = urllib2.urlopen(release_file)
    except HTTPError, e:        
        print "Error %s : %s" % (e.code, release_file)    
        return 1 
    data = remote_file.read()
    remote_file.close()
    release_file = NamedTemporaryFile()
    release_file.write(data)       
    Release = DebianControlFile(release_file.name)
    architectures = Release['Architectures'].split()
    components = Release['Components'].split()
    Log.log ("Available architectures: %s" % architectures)
    Log.log ("Available components: %s" % components)

    # Check if the requested components are available
    if requested_components:
        for component in requested_components[:]:
            if component not in components:
                Log.print_("Requested unavailable component %s" 
                    % component)
                return 2 

    # Check if the requested architectures are available
    if requested_architectures:
        for architecture in requested_architectures[:]:
            if architecture not in architectures:
                Log.print_("Requested unavailable architecture %s" % \
                    architecture)
                return 2 
                
    components = requested_components or components
    architectures = requested_architectures or architectures
    version = Release['Version'] or suite

    # Now let's import the Packages file for each architecture
    for arch in architectures:
        for component in components:
            packagelist = \
                PackageList.query.filter_by( \
                    suite = suite, \
                    version = version, \
                    component = component, \
                    architecture = arch).first() \
                or \
                PackageList( \
                    suite = suite, \
                    version = version, \
                    component = component, \
                    origin = Release['Origin'], \
                    label = Release['Label'], \
                    architecture = arch, \
                    description = Release['Description'], \
                    date = Release['Date'] \
                    )            
            packages_file = "%s/dists/%s/%s/binary-%s/Packages.gz" \
                % (archive_url, suite, component, arch)
            import_packages_file(archive_url, packagelist, packages_file)
            packagelist = None


def import_packages_file(archive_url, packagelist, packages_file):
    """
    Imports packages information from a packages file
    """
    global force_rpool, check_last_modified
    Log.log("Downloading %s" % packages_file)
    try:
        remote_file = urllib2.urlopen(packages_file)
    except HTTPError, e:
        session.rollback() # Rollback the suite insert
        print "%s : %s" % (e.code, packages_file)
        return -1
    
    data = remote_file.read()
    remote_file.close()      
    
    # Uncompress the file contents
    tmpfile = NamedTemporaryFile(delete = False)
    tmpfile.write(data)
    tmpfile.close()
    f = gzip.open(tmpfile.name)
    data = f.read()
    f.close()
    os.unlink(tmpfile.name)

    # Save the plain data to a temporary file
    tmpfile = NamedTemporaryFile(delete = False)
    tmpfile.write(data)
    tmpfile.close()
        
    keep_packages_list = [] # info from packages loaded from the file
    control = DebianControlFile(tmpfile.name)
    if not control['Package']:
        print "No packages defined at", packages_file
        return
    step = 1
    while step:
        package_name = control['Package']
        source = control['Source']
        version = control['Version']
        architecture = control['Architecture']
        description = control['Description'].split('\n')[0].decode('utf-8')                
        homepage = control['homepage']

        package = Package.query.filter_by( \
            package = package_name, \
            version = version, \
            architecture = architecture).first()
        if not package: # New package            
            deb_filename = "%s/%s" % (archive_url, control['Filename'])
            if force_rpool:
                deb_filename = deb_filename.replace("pool", "rpool", 1)
            if check_last_modified:
                last_modified = get_last_mofified_time(deb_filename)
            else:
                last_modified = datetime.now()
            is_visible = check_visibility(package_name, check_list)                
            Log.print_("Inserting %s %s %s %s visible=%s" % (package_name, source \
                , version, architecture, is_visible))
            package = Package( 
                package = package_name 
                , source = source 
                , version = version
                , architecture = architecture
                , last_modified = last_modified
                , description = description
                , homepage = homepage
                , is_visible = is_visible
            )
            #session.flush()
        # Create relation if needed
        if not packagelist in package.lists:
            Log.print_("Including %s -> %s" % (package, packagelist))
            package.lists.append(packagelist)
        # Add to in memory list to skip removal
        keep_packages_list.append("%s %s %s" % 
            (package.package, package.version, package.architecture))
        step = control.step()
    
            
    # Remove all relations to packages which were not imported
    # on the loop above
    must_remove = []
    for package in packagelist.packages:
        list_item = "%s %s %s" % (package.package, package.version \
            , package.architecture)            
        if list_item in keep_packages_list:
            keep_packages_list.remove(list_item)
        else:
            Log.print_("Removing %s" % `package`)
            must_remove.append(package)        
    for package in must_remove:
        packagelist.packages.remove(package)
    session.commit()
    os.unlink(tmpfile.name)
# We set the database engine here
def attach_to_db(db_url, echo=False):
    metadata.bind = db_url        
    metadata.bind.echo = echo 
    setup_all(True)     

def create_check_visibility_list(check_file):
    check_list = list()
    if check_file:
        for line in open(check_file):   
            if not line.strip():    
                continue        
            if line.startswith("#"):
                continue
            check_list.append(re.compile(line.strip()))
    return check_list
                                                                                                                                
def check_visibility(package, check_list):
    visibility = True                                                       
    for check in check_list:
        match = check.search(package)
        if match:
            visibility = False
            break
    return visibility    
        
def main():
    global force_rpool, check_last_modified, check_list
    parser = OptionParser()
    parser.add_option("-d", "--database",
        action = "store", type="string", dest="database",
        help = "specificy the database URI\n\n" \
        "Examples\n\n" \
        "   mysql://user:password@localhost/apt2sql" \
        "   sqlite:///apt2sql.db" \
    )
    parser.add_option("-c", "--check_visibility",
        action = "store", type="string", dest="check_file",
        help = "specificy text file containig regexp to exclude packages\n\n" \
        )            
    parser.add_option("-f", "--force-rpool",
        action = "store_true", dest="rpool", default=False,
        help = "force to use rpool path instead of pool")                
    parser.add_option("-m", "--get-last-modified",
        action = "store_true", dest="check_last_modified", default=False,
        help = "get the last modified info for .deb files")            
    parser.add_option("-q", "--quiet",
        action = "store_false", dest="verbose", default=True,
        help = "don't print status messages to stdout")
    parser.add_option("-r", "--recreate-tables",
        action = "store_true", dest="recreate_tables", default=False,
        help = "recreate db tables")                    
    parser.add_option("-s", "--sql-echo",
        action = "store_true", dest="sql_echo", default=False,
        help = "echo the sql statements")
    (options, args) = parser.parse_args()
    db_url = options.database or "sqlite:///apt2sql.db"
    if db_url == 'stdin': # special case to request from stdin (secure)
        db_url = raw_input('Please enter the db url:')
        print
    check_list = create_check_visibility_list(options.check_file)
    if len(args) < 2:
        print "Usage: %s " \
            "archive_root_url suite [component1[, component2] ]" \
            % os.path.basename(__file__)
        sys.exit(2)

    archive_url = args[0]
    suite = args[1]
    components = None
    architectures = None
    if len(args) > 2:
        if args[2] != "*":
            components = args[2].split(",")    
    if len(args) > 3:
        architectures = args[3].split(",")    

    Log.verbose = options.verbose        
    force_rpool = options.rpool
    check_last_modified = options.check_last_modified
    try:
        db_url_md5 = md5.new(db_url)
        lock = LockFile("apt2sql_%s" % db_url_md5 .hexdigest())
    except LockFile.AlreadyLockedError:
        Log.log("Unable to acquire lock, exiting")
        return

    attach_to_db(db_url, options.sql_echo)
    
    if options.recreate_tables:
        drop_all()
        setup_all(True)

    import_repository(archive_url, suite, components, architectures )
        
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'User requested interrupt'
        sys.exit(1)
