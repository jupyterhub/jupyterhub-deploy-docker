c = get_config()
import os

# This file is copied to /etc/jupyter in the docker image.
# This file just needs to point jupyter to the right course directory. You can have one more config file in the course home directory with other configuration.
c.CourseDirectory.root = os.environ['COURSE_HOME_ON_CONTAINER']

