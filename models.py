#!/usr/bin/python3
# from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime


db = SQLAlchemy()

# CREATE TABLE `data` (
#   `camera_id` varchar(255) NOT NULL,
#   `camera_loc` varchar(255) NOT NULL,
#   `capture_time` datetime NOT NULL DEFAULT current_timestamp(),
#   `frame` blob NOT NULL,
#   `frame_id` int(11) NOT NULL
# ) ENGINE=MyISAM DEFAULT CHARSET=latin1;


class Data(db.Model):
    __tablename__ = "data"
    camera_id = db.Column(db.String(255),nullable=False)
    camera_loc = db.Column(db.String(255),nullable=False)
    capture_time = db.Column(db.DateTime, default=datetime.datetime.now)
    image_path = db.Column(db.String(255),nullable=False)
    frame_id = db.Column(db.Integer,primary_key=True)


# CREATE TABLE `results` (
#   `obj_id` int(11) NOT NULL,
#   `frame_id` int(11) NOT NULL,
#   `label` varchar(50) NOT NULL,
#   `prob` varchar(10) NOT NULL,
#   `x` varchar(25) NOT NULL,
#   `y` varchar(25) NOT NULL,
#   `w` varchar(25) NOT NULL,
#   `h` varchar(25) NOT NULL
# ) ENGINE=MyISAM DEFAULT CHARSET=latin1;


class Result(db.Model):
    __tablename__ = "results"
    obj_id = db.Column(db.Integer,primary_key=True)
    frame_id = db.Column(db.Integer,nullable=False)
    label = db.Column(db.String(50))
    prob = db.Column(db.String(10),nullable=False)
    x = db.Column(db.String(25),nullable=False)
    y = db.Column(db.String(25),nullable=False)
    w = db.Column(db.String(25),nullable=False)
    h = db.Column(db.String(25),nullable=False)
    # rel=db.relationship('Data',foreign_keys='Result.frame_id')

    
