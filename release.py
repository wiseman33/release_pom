from git import Repo
from xml.etree.ElementTree import XMLParser, TreeBuilder, parse
import re


pom_path = 'pom.xml'
new_version = ''

def increase_version(version):
    # assume version is in format 0.0.0
    numbers = version.split('.')
    for index, num in enumerate(reversed(numbers)):
        current_index = len(numbers) - index -1
        if int(num) < 9:
            numbers[current_index] = str(int(num) + 1)
            for index in range(current_index + 1, len(numbers)):
                numbers[index] = '0'
            return '.'.join(numbers)
        
def update_pom_version():
    from xml.etree import ElementTree as et
    ns = "http://maven.apache.org/POM/4.0.0"
    et.register_namespace('', ns)
    ctb = TreeBuilder(insert_comments=True)
    xp = XMLParser(target=ctb)
    tree = et.ElementTree()
    tree.parse(pom_path, parser=xp)
    current_version = tree.getroot().find("{%s}version" % ns)
    global new_version
    new_version = increase_version(current_version.text)
    print('Updating pom.xml from {0} to {1}'.format(current_version.text, new_version))
    current_version.text = new_version
    tree.write(pom_path)
    
# update app version in pom.xml
update_pom_version()

repo = Repo('.')
commits = repo.iter_commits()

new_jiras = {}

if repo.tags:
    for commit in commits:
        # fetching all commits since last tag
        if commit == repo.tags[0].commit:
            break
        # extract only jiras numbers
        # assume commit message have to have jira number in format XX-00000
        jiras = re.findall("^[A-Z]{2}-[0-9]{5}", commit.message)
        # distinct jira numbers
        if jiras:
            if jiras[0] not in new_jiras:
                new_jiras[jiras[0]] = commit.message
        
new_tag_message = ';'.join(str(key) for key in new_jiras)

print('Jiras included to release: {0}'.format(new_tag_message))

tag_name = 'Release_{0}'.format(new_version)
print('Creating release tag {0} ...'.format(tag_name))

new_tag = repo.create_tag(tag_name)
repo.remotes.origin.push(new_tag, message=new_tag_message)
