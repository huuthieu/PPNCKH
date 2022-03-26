from pycocotools.coco import COCO
import numpy as np
import skimage.io as io
import matplotlib.pyplot as plt
import os
import tqdm
import cv2
import threading
import time

def download_image_id(save_path, id):
    """download image by id"""

    img = coco.loadImgs(id)[0]
    # img = coco.loadImgs(imgIds[np.random.randint(0,len(imgIds))])[0]
    img_name = os.path.basename(img['file_name'])
    I = io.imread(img['coco_url'])
    plt.imsave(os.path.join(save_path,img_name), I)

class Download(threading.Thread):
    def __init__(self,save_path, ids):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.ids = ids
        self.save_path = save_path
    def stop(self):
        self.stop_event.set()
    def run(self):
        for id in tqdm.tqdm(self.ids):
            download_image_id(self.save_path, id)

def download_image_multithread(save_path, nms, num_ids, num_thread):
    """download image using multithread
    Args:
        nms: list of category names
    """
    num_ids_per_thread = int(num_ids/num_thread)
    for class_name in nms:
        catIds = coco.getCatIds(catNms=['person']);
        imgIds = coco.getImgIds(catIds=catIds );
        # imgIds = imgIds[10000:60000]

        tasks = []
        for i in range(num_thread):
            tasks.append(Download(save_path = save_path, ids = imgIds[num_ids_per_thread*i:num_ids_per_thread*(i+1)]))
        # for task in tasks:
        #     task.stop()
        for t in tasks:
            t.start()

        time.sleep(10000)
        
        for task in tasks:
            task.join()

if __name__ == "__main__":
    dataDir='.'
    dataType='val2017'
    annFile='{}/annotations/instances_{}.json'.format(dataDir,dataType)

    coco=COCO(annFile)
    cats = coco.loadCats(coco.getCatIds())
    nms=[cat['name'] for cat in cats]
    print('COCO categories: \n{}\n'.format(' '.join(nms)))

    # nms = set([cat['supercategory'] for cat in cats])
    # print('COCO supercategories: \n{}'.format(' '.join(nms)))
    # # get all images containing given categories, select one at random
    save_path = 'val_coco_image'
    num_ids = 1000
    num_thread = 5
    download_image_multithread(save_path, nms, num_ids, num_thread)

