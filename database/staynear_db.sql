DROP DATABASE IF EXISTS staynear_db;


CREATE DATABASE staynear_db;

USE staynear_db;

SHOW DATABASES;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    profile_image VARCHAR(255) DEFAULT 'default_user.png',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE owners (
    owner_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    profile_image VARCHAR(255) DEFAULT 'default_owner.png',
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE amenities (
    amenity_id INT AUTO_INCREMENT PRIMARY KEY,
    amenity_name VARCHAR(50) NOT NULL UNIQUE
);

SHOW TABLES;

INSERT INTO amenities (amenity_name) VALUES
('WiFi'),
('Parking'),
('Laundry'),
('Food'),
('AC'),
('Gym'),
('CCTV'),
('Water Purifier'),
('Power Backup'),
('Lift'),
('Attached Bathroom'),
('Study Table'),
('Cupboard'),
('Hot Water'),
('Security Guard'),
('Canteen');

SELECT * FROM amenities;

CREATE TABLE properties (
    property_id INT AUTO_INCREMENT PRIMARY KEY,

    owner_id INT NOT NULL,

    property_name VARCHAR(150) NOT NULL,

    property_type ENUM('Hostel','PG','Flat','Room') NOT NULL,

    address TEXT NOT NULL,

    city VARCHAR(100) NOT NULL,

    pincode VARCHAR(10),

    latitude DECIMAL(10,8),

    longitude DECIMAL(11,8),

    monthly_rent DECIMAL(10,2) NOT NULL,

    security_deposit DECIMAL(10,2) DEFAULT 0,

    available_rooms INT DEFAULT 1,

    description TEXT,

    verified BOOLEAN DEFAULT FALSE,

    available BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (owner_id)
        REFERENCES owners(owner_id)
        ON DELETE CASCADE
);

DESCRIBE properties;

CREATE TABLE property_images (

    image_id INT AUTO_INCREMENT PRIMARY KEY,

    property_id INT NOT NULL,

    image_path VARCHAR(255) NOT NULL,

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(property_id)
        REFERENCES properties(property_id)
        ON DELETE CASCADE
);

ALTER TABLE properties
ADD property_status ENUM('Pending','Approved','Rejected')
DEFAULT 'Pending';

ALTER TABLE properties
DROP COLUMN verified;

SHOW TABLES;

CREATE TABLE property_amenities (
    property_id INT NOT NULL,
    amenity_id INT NOT NULL,

    PRIMARY KEY (property_id, amenity_id),

    FOREIGN KEY (property_id)
        REFERENCES properties(property_id)
        ON DELETE CASCADE,

    FOREIGN KEY (amenity_id)
        REFERENCES amenities(amenity_id)
        ON DELETE CASCADE
);

CREATE TABLE wishlist (
    wishlist_id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    property_id INT NOT NULL,

    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    FOREIGN KEY (property_id)
        REFERENCES properties(property_id)
        ON DELETE CASCADE,

    UNIQUE(user_id, property_id)
);

CREATE TABLE bookings (

    booking_id INT AUTO_INCREMENT PRIMARY KEY,

    property_id INT NOT NULL,

    user_id INT NOT NULL,

    visit_date DATE NOT NULL,

    visit_time TIME NOT NULL,

    message TEXT,

    booking_status ENUM(
        'Pending',
        'Approved',
        'Rejected',
        'Completed'
    ) DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(property_id)
        REFERENCES properties(property_id)
        ON DELETE CASCADE,

    FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE reviews (

    review_id INT AUTO_INCREMENT PRIMARY KEY,

    property_id INT NOT NULL,

    user_id INT NOT NULL,

    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),

    review TEXT,

    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(property_id)
        REFERENCES properties(property_id)
        ON DELETE CASCADE,

    FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE notifications (

    notification_id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    title VARCHAR(100),

    message TEXT,

    is_read BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE property_reports (

    report_id INT AUTO_INCREMENT PRIMARY KEY,

    property_id INT NOT NULL,

    user_id INT NOT NULL,

    reason TEXT NOT NULL,

    report_status ENUM(
        'Pending',
        'Reviewed',
        'Resolved'
    ) DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(property_id)
        REFERENCES properties(property_id)
        ON DELETE CASCADE,

    FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

INSERT INTO admins (username, password)
VALUES
('admin', 'admin123');

INSERT INTO owners (full_name, email, password, phone, verified)
VALUES
('Rahul Sharma', 'rahul.sharma@gmail.com', 'owner123', '9876543210', TRUE),
('Priya Patil', 'priya.patil@gmail.com', 'owner123', '9876543211', TRUE),
('Amit Kulkarni', 'amit.kulkarni@gmail.com', 'owner123', '9876543212', TRUE);

INSERT INTO users (full_name, email, password, phone)
VALUES
('Vaibhav Joshi', 'vaibhav@gmail.com', 'user123', '9876500001'),
('Sneha Patil', 'sneha@gmail.com', 'user123', '9876500002'),
('Rohan Shah', 'rohan@gmail.com', 'user123', '9876500003'),
('Pooja Deshmukh', 'pooja@gmail.com', 'user123', '9876500004'),
('Karan Mehta', 'karan@gmail.com', 'user123', '9876500005');

INSERT INTO properties
(
owner_id,
property_name,
property_type,
address,
city,
pincode,
latitude,
longitude,
monthly_rent,
security_deposit,
available_rooms,
description,
property_status,
available
)
VALUES

(
1,
'Sunrise PG',
'PG',
'College Road',
'Nashik',
'422005',
19.997500,
73.789800,
6500,
10000,
5,
'Comfortable PG with WiFi and meals for students.',
'Approved',
TRUE
),

(
1,
'Green Valley Hostel',
'Hostel',
'Gangapur Road',
'Nashik',
'422013',
20.005200,
73.760500,
4500,
5000,
10,
'Affordable hostel near engineering colleges.',
'Approved',
TRUE
),

(
2,
'City View Apartment',
'Flat',
'Canada Corner',
'Nashik',
'422002',
19.991400,
73.776700,
14000,
25000,
2,
'2BHK furnished apartment suitable for families.',
'Approved',
TRUE
),

(
2,
'Budget Stay Rooms',
'Room',
'Panchavati',
'Nashik',
'422003',
20.010500,
73.789200,
3500,
3000,
4,
'Affordable single rooms for students.',
'Approved',
TRUE
),

(
3,
'Royal Residency PG',
'PG',
'Mahatma Nagar',
'Nashik',
'422007',
19.981000,
73.770000,
7500,
12000,
6,
'Premium PG with food and security.',
'Approved',
TRUE
),

(
3,
'Comfort Nest Hostel',
'Hostel',
'Indira Nagar',
'Nashik',
'422009',
19.968400,
73.783000,
5000,
6000,
8,
'Modern hostel with study rooms.',
'Approved',
TRUE
),

(
2,
'Lake View Flat',
'Flat',
'CIDCO',
'Nashik',
'422009',
19.960500,
73.790400,
12000,
20000,
1,
'Peaceful flat with balcony view.',
'Approved',
TRUE
),

(
1,
'Student Hub PG',
'PG',
'Untwadi',
'Nashik',
'422008',
19.987200,
73.781900,
6800,
9000,
5,
'Student-focused PG near coaching classes.',
'Approved',
TRUE
),

(
3,
'Elite Rooms',
'Room',
'Dwarka',
'Nashik',
'422011',
19.994300,
73.798100,
4200,
5000,
3,
'Private rooms with attached bathroom.',
'Approved',
TRUE
),

(
2,
'Shree Hostel',
'Hostel',
'Satpur',
'Nashik',
'422012',
19.956900,
73.748700,
4700,
5000,
9,
'Hostel with spacious rooms and WiFi.',
'Approved',
TRUE
);

INSERT INTO property_images (property_id, image_path)
VALUES

(1,'uploads/properties/property_1/image1.jpg'),
(1,'uploads/properties/property_1/image2.jpg'),

(2,'uploads/properties/property_2/image1.jpg'),
(2,'uploads/properties/property_2/image2.jpg'),

(3,'uploads/properties/property_3/image1.jpg'),
(3,'uploads/properties/property_3/image2.jpg'),

(4,'uploads/properties/property_4/image1.jpg'),
(5,'uploads/properties/property_5/image1.jpg'),
(6,'uploads/properties/property_6/image1.jpg'),
(7,'uploads/properties/property_7/image1.jpg'),
(8,'uploads/properties/property_8/image1.jpg'),
(9,'uploads/properties/property_9/image1.jpg'),
(10,'uploads/properties/property_10/image1.jpg');

DELETE FROM property_amenities;

DELETE FROM amenities;

ALTER TABLE amenities AUTO_INCREMENT = 1;

INSERT INTO amenities (amenity_name)
VALUES
('WiFi'),
('Parking'),
('Laundry'),
('Food'),
('AC'),
('Gym'),
('CCTV'),
('Water Purifier'),
('Power Backup'),
('Lift'),
('Attached Bathroom'),
('Study Table'),
('Cupboard'),
('Hot Water'),
('Canteen'),
('Security Guard');

INSERT INTO property_amenities (property_id, amenity_id)
VALUES

-- Property 1 : Sunrise PG
(1,1),   -- WiFi
(1,3),   -- Laundry
(1,4),   -- Food
(1,7),   -- CCTV
(1,11),  -- Attached Bathroom
(1,12),  -- Study Table
(1,13),  -- Cupboard

-- Property 2 : Green Valley Hostel
(2,1),
(2,2),
(2,3),
(2,7),
(2,9),
(2,15),

-- Property 3 : City View Apartment
(3,1),
(3,2),
(3,5),
(3,8),
(3,10),
(3,11),

-- Property 4 : Budget Stay Rooms
(4,1),
(4,7),
(4,11),
(4,13),

-- Property 5 : Royal Residency PG
(5,1),
(5,4),
(5,5),
(5,7),
(5,14),
(5,15),

-- Property 6 : Comfort Nest Hostel
(6,1),
(6,2),
(6,3),
(6,4),
(6,6),
(6,7),
(6,9),
(6,15),

-- Property 7 : Lake View Flat
(7,1),
(7,2),
(7,5),
(7,8),
(7,10),
(7,11),

-- Property 8 : Student Hub PG
(8,1),
(8,3),
(8,4),
(8,7),
(8,12),
(8,13),

-- Property 9 : Elite Rooms
(9,1),
(9,5),
(9,7),
(9,11),
(9,13),

-- Property 10 : Shree Hostel
(10,1),
(10,2),
(10,3),
(10,4),
(10,7),
(10,9),
(10,15);

INSERT INTO wishlist (user_id, property_id)
VALUES
(1,1),
(1,5),
(2,3),
(3,2),
(4,8),
(5,10);

INSERT INTO bookings
(property_id, user_id, visit_date, visit_time, message, booking_status)
VALUES

(1,1,'2026-08-10','10:00:00','Interested in seeing the room.','Pending'),

(3,2,'2026-08-11','11:30:00','Need family accommodation.','Approved'),

(5,3,'2026-08-12','03:00:00','Looking for PG near college.','Completed'),

(2,4,'2026-08-13','02:00:00','Want to check hostel facilities.','Rejected'),

(8,5,'2026-08-15','04:30:00','Need accommodation urgently.','Pending');

INSERT INTO reviews
(property_id,user_id,rating,review)
VALUES

(5,3,5,'Excellent PG with tasty food and clean rooms.'),

(3,2,4,'Nice apartment and good locality.'),

(1,1,5,'Very comfortable stay and helpful owner.'),

(2,4,3,'Affordable but rooms are a little small.');

INSERT INTO notifications
(user_id,title,message)
VALUES

(1,'Booking Submitted',
'Your visit request has been submitted successfully.'),

(2,'Booking Approved',
'Your visit request has been approved by the owner.'),

(3,'Review Posted',
'Thank you for sharing your review.'),

(4,'Booking Rejected',
'The owner rejected your visit request.'),

(5,'Welcome to StayNear',
'Thank you for registering on StayNear.');

INSERT INTO property_reports
(property_id,user_id,reason,report_status)
VALUES

(2,5,'Incorrect rent information mentioned.','Pending'),

(4,2,'Owner is not responding.','Reviewed');


SELECT * FROM admins;
SELECT * FROM owners;
SELECT * FROM users;
SELECT * FROM amenities;
SELECT * FROM properties;
SELECT * FROM property_images;
SELECT * FROM property_amenities;
SELECT * FROM wishlist;
SELECT * FROM bookings;
SELECT * FROM reviews;
SELECT * FROM notifications;
SELECT * FROM property_reports;