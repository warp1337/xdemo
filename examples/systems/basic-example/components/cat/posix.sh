#!/bin/bash

function start {
    cat /tmp/xdemo_client/$USER/logs/xdemo_component_*
}

function hook_check {
    true
}

function hook_stop {
    true
}