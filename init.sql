create database users;

create table users (
	username text not null,
    password text not null
);


-- ALTER TABLE vendors
-- ADD COLUMN phone VARCHAR(15) AFTER name;

-- ALTER TABLE Orders
-- ADD FOREIGN KEY (PersonID) REFERENCES Persons(PersonID);