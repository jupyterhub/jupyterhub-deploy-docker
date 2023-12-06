"""
Example JupyterHub config allowing users to specify environment variables and notebook-server args
"""
import shlex
from dockerspawner import DockerSpawner

class CustomDockerSpawner(DockerSpawner):
    def _options_form_default(self):
    # def _default_options_form(self):
        from jinja2 import Environment, FileSystemLoader

        environment = Environment(loader=FileSystemLoader("templates/"))
        template = environment.get_template("post_login_select_image_form.html.j2")

        obj = dict(
            username = self.user.name,
            images = self.allowed_images
        )

        return template.render(**obj)

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
