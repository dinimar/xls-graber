import concurrent.futures
import configparser
import logging
import os
from queue import Queue

import requests
from lxml import html

import utils.grab_lib as graber

# create logger
cli_logger = logging.getLogger('i-otvet-graber')
# set logging level
cli_logger.setLevel(logging.DEBUG)
# create console and file handler
ch = logging.StreamHandler()
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to handlers
ch.setFormatter(formatter)
# add handlers to logger
cli_logger.addHandler(ch)

config_file = "graber.ini"
config = configparser.ConfigParser()
config.read(os.path.join(graber.root, config_file))

th_num = int(config["th_config"]["th_num"])
save_coef = int(config["general"]["save_coef"])
q_list_page_num = int(config["general"]["q_list_page_num"])
last_page_num = 0

link_pool = Queue(maxsize=q_list_page_num)
# link_pool.put(next_page) remove cause it equals next_page+"?start="+str(0))
que_pool = Queue(q_list_page_num * 20 + 1) # 1 redundant cell for 'poison element'

# qs_x = "//div[contains(@class, 'qa-q-list')]/div[contains(@class, 'qa-q-list-item')]" \
#        "/div[contains(@class, 'qa-q-item-main')]/div[contains(@class, 'qa-q-item-title')]/a"

pr_num = 1 # to satisfy xls requirements



# q_list = []
# a_list = []

# link_pool = graber.init_link_pool(link_pool, q_list_page_num)
for i in range(q_list_page_num):
    link_pool.put(str(graber.next_page + "?start=" + str(i*20)))


def get_tree(link):
    data = requests.get(link)  # bytes
    return html.fromstring(data.content.decode('utf-8'))


def prod_q_links(i):
    global que_pool
    global pr_num

    while not link_pool.empty():
        # tree = get_tree(link_pool.get())
        link_pool.task_done()
        # qs = tree.xpath(qs_x)
        for q in graber.process_list_page(link_pool.get()):
            que_pool.put((graber.create_q_link(q), pr_num)) # you should add in queue link with its id to prevent id collision in csv
            pr_num = pr_num + 1
        # print("("+str(i)+")Produced page to p_queue:"+str(pr_num))

    if pr_num == q_list_page_num*20 + 1: # cause initial pr_num = 1
        # print("-------------------------------------------------------------Producer put poison")
        que_pool.put((None, None))

    cons_q_link(i)


def cons_q_link(i):
    global que_pool
    global last_page_num
    while True:
        data, q_id = que_pool.get()
        if (data is None) and (q_id is None): # check if it poison pill
            que_pool.task_done()
            que_pool.put((data, q_id)) # return poison pill to make other consumers stop
            break
        else:
            # tree = get_tree(data)
            try:
                graber.process_q_page(data, q_id)
                que_pool.task_done()
                last_page_num = last_page_num + 1
                # print("Consumed: "+str(last_page_num))
                if (last_page_num % save_coef == 0) and (last_page_num != 0):
                    graber.create_q_csv(last_page_num)
                if (last_page_num % save_coef*100 == 0):
                    graber.create_c_csv()
            finally:
                pass


cli_logger.info("Start: " + str(q_list_page_num*20))

try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=th_num) as executor:
        for index in range(int(th_num/2)):
            executor.submit(prod_q_links, index)
            executor.submit(cons_q_link, index)
finally:
    # graber.save(q_list_page_num * 20)
    graber.create_c_csv()
    cli_logger.info("Finish.")
