update user set auth = 1 where id = 1;
insert into user_group (id, name) VALUES ( 1, 'Admin' );
insert into user_group_members (user_id, user_group_id ) VALUES ( 1,1);
insert into application_category (id, name) VALUES (1,'FPS') ;
insert into application (id, name, homepage, descr, license, note, source_package, category_id ) VALUES ( 1, 'FPS 1', 'http://fps1.eu', 'Descr', 'GPL3', 'Note', 'fps1', 1 );
insert into application (id, name, homepage, descr, license, note, source_package, category_id ) VALUES ( 2, 'FPS 2', 'http://fps2.eu', 'Descr 2', 'GPL3', 'Note', 'fps2', 1 );
insert into packagelist (id, origin, suite, version, component, architecture, label, description, date ) values ( 1 ,'GetDeb','vivid-getdeb','15.04','apps','amd64','GetDeb','GetDeb packages', datetime('now') );
insert into package (id, package, source, version, architecture, last_modified, description, homepage, install_class, is_visible, download_count) VALUES(1, 'fps1', NULL, '1.01', 'amd64', datetime('now'), 'Description FPS1 from package', 'package homepage fps1', NULL, 1, 0 );
insert into packagelist_members (packagelist_id, package_id) VALUES (1,1);
insert into package (id, package, source, version, architecture, last_modified, description, homepage, install_class, is_visible, download_count) VALUES(2, 'fps2', NULL, '1.02', 'amd64', datetime('now'), 'Description FPS2 from package', 'package homepage fps2', NULL, 1, 0 );
insert into packagelist_members (packagelist_id, package_id) VALUES (1,2);

