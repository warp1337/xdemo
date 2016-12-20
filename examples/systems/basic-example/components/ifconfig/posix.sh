#!/bin/bash

function start {
    /sbin/ifconfig
}

function hook_check {
    true
}

function hook_stop {
    true
}