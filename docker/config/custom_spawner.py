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

