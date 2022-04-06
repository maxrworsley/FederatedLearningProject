#!/bin/bash
gnome-terminal --tab --title="Node_1" --command="bash -c 'docker run -it --rm -p 127.0.0.1:40301:40400 fls_node:1.0; $SHELL'"
gnome-terminal --tab --title="Node_2" --command="bash -c 'docker run -it --rm -p 127.0.0.1:40302:40400 fls_node:1.0; $SHELL'"
gnome-terminal --tab --title="Node_3" --command="bash -c 'docker run -it --rm -p 127.0.0.1:40303:40400 fls_node:1.0; $SHELL'"