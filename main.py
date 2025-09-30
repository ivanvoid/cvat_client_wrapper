from cvat_client import CVATClient
import os

def example_1(cvat_writer):
    '''
    Create new PROJECT and populate it with new TASK
    '''
    # Create project
    project_name = 'New Test Project 1'
    project_labels = ['car', 'cat', 'dog']

    project = cvat_writer.create_project(project_name, project_labels)

    # Upload images
    images_path = ['./test_imgs/'+f for f in os.listdir('./test_imgs')]

    task = cvat_writer.create_task(project.id, images_path, project_name)

    # Upload BBOX annotations
    bboxes = {
        0:[[0,0,10,10], [20,20,90,90]], # all boxes for one image
        1:[[0,0,15,15], [50,10,60,60]]
    }
    labels = {
        0:['car', 'cat'], # labels of those boxes
        1:['dog', 'dog']
    }

    cvat_writer.upload_bbox(task, bboxes, labels)


    '''
    Create new TASK in existing PROJECT 
    '''
    print('All projects:\n',cvat_writer.get_projects())
    last_project = cvat_writer.get_projects()[-1]
    # project = cvat_writer.get_project(ID=last_project.id)

    taks_name = 'New Task In existing project'

    print('Creating new task in project ',last_project.id)
    task = cvat_writer.create_task(project.id, images_path, taks_name)

    '''
    Upload BBOX annotations to existing last TASK
    '''
    # import inspect;import pdb;pdb.set_trace() #inspect.signature

    task = cvat_writer.get_tasks()[-1]
    print('Uploading annotations to task ',task.id,' ...')
    cvat_writer.upload_bbox(task, bboxes, labels)
    
    '''
    Upload polygons into last PROJECT
    '''
    # Polygon annotations
    import numpy as np
    N = 1000
    points = [coord for i in range(N) for coord in (200 + 100 * np.cos(2 * np.pi * i / N), 200 + 100 * np.sin(2 * np.pi * i / N))]
    points = [int(p) for p in points]
    
    print(f'Downsample poly with {N} points')
    points = cvat_writer.downsample_poly(points)
    print(f'New sample size: {len(points)/2}')

    polygons = {
        0:[[3, 2, 2, 3, 3, 4], [30, 20, 20, 30, 30, 40]],
        1:[points],
    }
    labels={
        0:['car', 'cat'],
        1:['dog']
    }
    
    task = cvat_writer.create_task(project.id, images_path, 'New Poly Task')
    cvat_writer.upload_poly(task, polygons, labels)


    '''
    Download project as dataset
    '''
    print(f'Downloading Project {last_project.id} into: ./project{last_project.id}.zip')
    cvat_writer.download_project(
        ID=last_project.id,
        filepath=f'./project{last_project.id}.zip',
        format_name=cvat_writer.EXPORT_FORMATS[-1] # YOLO
    )

def example_2(cvat_writer):
    '''
    Upload COCO annotations to a specific task
    '''
    # Job 82
    # Task 92
    # Project 57
    project = cvat_writer.get_project(57)
    task = cvat_writer.get_task(92)

    annotations_coco_path = '/home/noc/projects/cvat_client/instances_default.json'
    task.import_annotations('COCO 1.0',annotations_coco_path)


def main():
    '''
    Connect to CVAT
    '''
    host = '10.127.0.146'
    port = '8080'
    login = 'cvat_test'
    password = 'QWERTY123q'

    cvat_writer = CVATClient(
        host,port,
        login, password
    )

    # Example itself might be broken due to task not existing but logic should still work
    # example_1(cvat_writer)
    example_2(cvat_writer)



main()
print('done.')