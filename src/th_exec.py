import concurrent.futures
import requests
from lxml import html
from threading import Thread
from queue import Queue
import logging

# create logger
cli_logger = logging.getLogger('i-otvet-parser')
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

host = "https://i-otvet.ru"
next_page = host + "/questions"
last_page_num = 10925381
q_list_page_num = 50

link_pool = Queue(maxsize=q_list_page_num)
# link_pool.put(next_page) remove cause it equals next_page+"?start="+str(0))
p_queue = Queue(q_list_page_num*20+1) # 1 redundant cell for 'poison element'

qs_x = "//div[contains(@class, 'qa-q-list')]/div[contains(@class, 'qa-q-list-item')]" \
       "/div[contains(@class, 'qa-q-item-main')]/div[contains(@class, 'qa-q-item-title')]/a"

last_page_num = q_list_page_num*20
pr_num = con_num = 1

con_flag = True


def get_tree(link):
    data = requests.get(link)  # bytes
    return html.fromstring(data.content.decode('utf-8'))


for i in range(q_list_page_num):
    link_pool.put(str(next_page + "?start=" + str(i*20)))


def prod_q_links(i):
    global p_queue
    global pr_num
    global con_flag

    while not link_pool.empty():
        tree = get_tree(link_pool.get())
        link_pool.task_done()
        qs = tree.xpath(qs_x)
        for q in qs:
            p_queue.put(host + q.attrib.get('href')[1:])
            print("("+str(i)+")Produced page to p_queue:"+str(pr_num))
            pr_num = pr_num + 1

    if pr_num == 1001: # the last producer have pr_num = 1000 and increase it by 1
                        # so we have pr_num=1001 at the end
        print("-------------------------------------------------------------Producer put poison")
        p_queue.put(None)


def cons_q_link(i):
    global p_queue
    global last_page_num
    global con_num
    global con_flag
    while con_flag:
        data = p_queue.get()
        if data is None: # check if it poison pill
            p_queue.task_done()
            p_queue.put(data) # return poison pill to make other consumers stop
            break
        else:
            tree = get_tree(data)
            p_queue.task_done()
            print("Consumed: "+str(i)+" - "+str(last_page_num))
            last_page_num = last_page_num - 1

    print("Consumer is dead ", str(i))


# producers = []
# consumers = []
cli_logger.info("Start")

with concurrent.futures.ThreadPoolExecutor(max_workers=4000) as executor:
    for index in range(2000):
        executor.submit(prod_q_links, index)
        executor.submit(cons_q_link, index)


cli_logger.info("Finish.")
