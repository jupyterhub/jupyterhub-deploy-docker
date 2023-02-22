"""
Example JupyterHub config allowing users to specify environment variables and notebook-server args
"""
import shlex

from dockerspawner import DockerSpawner


class CustomDockerSpawner(DockerSpawner):
    def _options_form_default(self):
        return """
        <div class="well">
            <h4>Welcome, {username}</h4>

            <p>This is a fully-featured
            <a href="https://wiki.europlanet-gmap.eu" target="_blank" title="JupyterLab">
                JupyterLab
            </a>
            environment;
            For details such as data persistence, data privacy and other policies please
            refer to the service's dedicated page in our public Wiki
            <a href="https://wiki.europlanet-gmap.eu" target="_blank" title="GMAP Wiki">
                <sup>[1]</sup>
            </a>
            </p>

            <p>The Jupyter Notebook about to run is an instance of a Docker container,
            isolated from other users but from the filesytem mounting points for
            data sharing and <em>work</em> directories persistence.
            <br>
            In the dropdown menu below, the list of available the Docker images
            to instanciate. For further details about the images (eg, software
            content, settings) and instructions on how to use the <em>same</em> image
            on your premises, check the GMAP DockerHub
            <a href="https://hub.docker.com/u/gmap" target="_blank" title="GMAP DockerHub">
                <sup>[2]</sup>
            </a>
            repositories.
            </p>
            <hr>
            <ol>
                <li>
                    <a href="https://wiki.europlanet-gmap.eu" target="_blank">
                        https://wiki.europlanet-gmap.eu
                    </a>
                </li>
                <li>
                    <a href="https://hub.docker.com/u/gmap" target="_blank">
                        https://hub.docker.com/u/gmap
                    </a>
                </li>
            </ol>
        </div>

        <div class="alert alert-info" role="alert">
            Make sure to read the <strong>README</strong> file (<code>README.md</code>)
            available at the <i>root</i> of your JupyterLab instance,
            it provides up-to-date information about the <i>running environment</i>
            and online documentation to <i>relevant resources</i>.
        </div>

        <div class="form-inline">
            <div class="form-group">
                <label for="image">Environment/Image to use:</label>
                <select class="form-control" name="image" id="image">
                    <option value="{image}" selected>{image}</option>
                </select>
            </div>
        </div>

        """.format(
            username=self.user.name,
            image=self.image
        )

    def options_from_form(self, formdata):
        options = {}
        image_form_list = formdata.get("image", [])
        if image_form_list and image_form_list[0]:
            options["image"] = image_form_list[0].strip()
            self.log.info(f"User selected image: {options['image']}")
        return options

    def load_user_options(self, options):
        image = options.get("image")
        if image:
            self.log.info(f"Loading image {image}")
            self.image = image
