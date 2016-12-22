#!/bin/bash

function start {
    echo "xdemoroot: " $XDEMOROOT
    echo "xdemoprefix: " $XDEMOPREFIX
}

function hook_check {
    true
}

function hook_stop {
    true
}