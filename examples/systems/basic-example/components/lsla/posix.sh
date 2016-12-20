#!/bin/bash

function start {
    ls -la $XDEMOROOT; ls -la $XDEMOPREFIX
}

function hook_check {
    true
}

function hook_stop {
    true
}