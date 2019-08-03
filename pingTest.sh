#!/bin/sh
pingTo=www.baidu.com
#pingTo=baidu.com
#pingTo=10.99.200.210
ping $pingTo -c 3 -W 1
