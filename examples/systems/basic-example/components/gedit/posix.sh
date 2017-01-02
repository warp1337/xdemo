#!/bin/bash

function start {
    /usr/bin/gedit &
}

function hook_check {
    true
}

function hook_stop {
    true
}