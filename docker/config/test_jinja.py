from jinja2 import Environment, FileSystemLoader

images = []
with open('imagelist', 'r') as fp:
    for entry in fp.readlines():
        entry = entry.strip()
        if entry and entry[0] != '#':
            images.append(entry)


environment = Environment(loader=FileSystemLoader("templates/"))
template = environment.get_template("post_login_select_image_form.html.j2")

content = template.render(username='carlos', images=images)

with open('test.html', 'w') as fp:
    fp.write(content)

