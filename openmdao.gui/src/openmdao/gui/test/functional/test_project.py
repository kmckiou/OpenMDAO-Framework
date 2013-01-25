import glob
import os
import time

from nose.tools import eq_ as eq
from nose.tools import with_setup

from util import main, setup_server, teardown_server, generate, \
                 begin, new_project, edit_project, get_browser_download_location_path, \
                 import_project


@with_setup(setup_server, teardown_server)
def test_generator():
    for _test, browser in generate(__name__):
        yield _test, browser


#Test creating a project
def _test_new_project(browser):

    browser_download_location_path = get_browser_download_location_path(browser)

    projects_page = begin(browser)

    # Create a project.
    projects_page, project_dict = new_project(projects_page.new_project(),
                                              verify=True, load_workspace=False)
    # Go back to projects page to see if it is on the list.
    assert projects_page.contains(project_dict['name'])

    # Make sure all the project meta data was saved correctly.
    edit_dialog = projects_page.edit_project(project_dict['name'])
    eq(str(edit_dialog.project_name).strip(), project_dict['name'])
    eq(str(edit_dialog.description).strip(), project_dict['description'])
    eq(str(edit_dialog.version).strip(), project_dict['version'])  # maxlength

    # Edit the project meta data
    project_dict['description'] = "pony express"
    project_dict['version'] = "23432"

    projects_page = edit_project(edit_dialog,
                         project_dict['name'],
                         project_dict['description'],
                         project_dict['version'],
                         load_workspace=False)

    # Make sure all the new project meta data was saved correctly.
    edit_dialog = projects_page.edit_project(project_dict['name'])
    eq(str(edit_dialog.project_name).strip(), project_dict['name'])
    eq(str(edit_dialog.description).strip(), project_dict['description'])
    eq(str(edit_dialog.version).strip(), project_dict['version'][:5])  # maxlength
    edit_dialog.cancel()

    # Export the project
    projects_page.export_project(project_dict['name'])
    time.sleep(1)  # give the download some time to complete
    # See if the file is in the downloads directory
    project_path = glob.glob(os.path.join(browser_download_location_path + "/" + project_dict['name'].replace(" ", "_")) + "*")
    assert (len(project_path) == 1)

    # Delete the project in preparation for reimporting
    projects_page.delete_project(project_dict['name'])

    # Make sure the project was deleted
    assert not projects_page.contains(project_dict['name'])

    # Import the project and give it a new name
    projects_page, project_dict = import_project(projects_page.import_project(), project_path,
                                              verify=True, load_workspace=False)
    # Go back to projects page to see if it is on the list.
    assert projects_page.contains(project_dict['name'])

    # remove the downloaded file
    os.remove(project_path[0])

if __name__ == '__main__':
    main()
