create table plan(
	id int AUTO_INCREMENT,
  name varchar(50),
  description varchar(255),
  usage_limit int,
  PRIMARY KEY (id)
);


insert into plan values(1, 'Basic', 'Allows a user to access the first layer endpoints only for a limited usage', 50),
                       (2, 'Intermediate', 'Allows a user to access the first and second layer endpoints only for a limited usage', 100),
                       (3, 'Advanced', 'Allows a user to access 3 layers of endpoints for a limited usage', 200),
                       (4, 'Prime', 'Allows a user to access all the endpoints for a unimited usage', 0);


create table endpoints(
	id int AUTO_INCREMENT,
  name varchar(50),
  api_endpoint varchar(50),
  description varchar(255),
  PRIMARY KEY (id)
);

insert into endpoints values(1, 'Storage Bucket', '/create-bucket', 'Creates a new storage'),
														(2, 'Storage Bucket', '/get-bucket', 'View the bucket'),
                            (3, 'Storage Bucket', '/delete-bucket', 'Delete a storage bucket'),
                            (4, 'Virtual Machine', '/create-vm', 'Creates a vm'),
														(5, 'Virtual Machine', '/get-vm', 'View the vm'),
                            (6, 'Virtual Machine', '/delete-vm', 'Delete a vm'),
                            (7, 'Logs', '/create-logs', 'Creates a new log file'),
														(8, 'Logs', '/get-logs', 'View the log file'),
                            (9, 'Logs', '/delete-logs', 'Delete a log file');
                            
create table subscription(
	id int AUTO_INCREMENT,
  user_id int,
  plan_id int,
  api_usage int,
  PRIMARY KEY (id)
);

create table plan_endpoints(
  plan_id int,
  api_id int,
  FOREIGN KEY (plan_id) REFERENCES plan(id),
  FOREIGN KEY (api_id) REFERENCES endpoints(id)
);

insert into plan_endpoints values(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(2,4),(2,5),(2,6),
																(3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7),(3,8),(3,9),
                                (4,1),(4,2),(4,3),(4,4),(4,5),(4,6),(4,7),(4,8),(4,9);

create table users(
	id int PRIMARY KEY AUTO_INCREMENT,
  username varchar(50),
  password varchar(50)
);












