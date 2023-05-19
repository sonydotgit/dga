"""
Starting capture network traffic and blocking hosts
"""
import logging
import pickle
import time
import tldextract
import iptc
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from scapy.all import *
from scapy.layers.dns import DNS
from scapy.layers.inet import IP
import numpy as np


def packet_callback(packet):
    global pre_domain
    global pred_result

    pred_result = 0

    if IP in packet:
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:
            qname = packet.getlayer(DNS).qd.qname.decode("utf-8")
            ext_qname = tldextract.extract(qname)
            print(ext_qname.domain)
            if len(ext_qname.domain) > 6 and "-" not in ext_qname.domain and ext_qname.domain != pre_domain:
                match = ngram_counts * vectorizer.transform([ext_qname.domain]).transpose()
                X_pred = [len(ext_qname.domain), match]
                X_pred = np.array(X_pred, dtype=object)
                print(X_pred)
                pre_domain = ext_qname.domain
                if clf.predict([X_pred]) == 'dga':
                    pred_result = 1
                    print(str(ip_src.encode("utf-8")) + ' --> ' + str(ip_dst.encode("utf-8")) + ' : ' + qname)
                    logger.info(str(ip_src.encode("utf-8")) + ' --> ' + str(ip_dst.encode("utf-8")) + ' : ' + qname)
                    # Check if ip source already exists
                    if ip_src in dga_hosts:
                        dga_hosts[ip_src] = dga_hosts[ip_src] + 1
                    # Add ip source to list and set value to 1
                    else:
                        dga_hosts[ip_src] = 1


def iptables(dga_hosts):
    # Block dangerous hosts, add rule in iptables (for current session)
    # Ignore possibly not dangerous hosts (occur < 10)
    logger.info("Blocked hosts:")
    for key, val in dga_hosts.items():
        if val >= 10:
            print("Blocking host with ip address: %s" % key)
            logger.info("IP address: %s" % key)
            chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
            rule = iptc.Rule()
            rule.src = key
            rule.target = iptc.Target(rule, "DROP")
            chain.insert_rule(rule)


def capture(progress_queue):
    global ngram_counts
    global vectorizer
    global clf
    global pre_domain
    global logger
    global dga_hosts

    progress_queue.put((10, "Loading dataset from disk..."))
    time.sleep(1)
    with open('input data/training_data.pkl', 'rb') as f:
        training_data = pickle.load(f)

    progress_queue.put((20, "Loading model from disk..."))
    time.sleep(1)
    clf = joblib.load('input data/model.pkl')

    progress_queue.put((30, "Loading and preparing necessary data for model"))
    # Repeat operations on count ngram counts
    vectorizer = CountVectorizer(ngram_range=(3, 5), analyzer='char', max_df=1.0, min_df=0.0001)
    ngram_matrix = vectorizer.fit_transform(training_data['legit']['domain'])
    ngram_counts = ngram_matrix.sum(axis=0).getA1()

    # Definition previous domain so that the domains not repeat in output console
    # Inasmuch as dns-server generate many additional packets during his work
    pre_domain = None

    # Collect counts dga query occurrences for separate hosts
    dga_hosts = {}

    print("List system interfaces: ", os.listdir('/sys/class/net/'))
    # interface = input("Enter desired interface: ")
    interface = 'wlan0'

    progress_queue.put((70, "Scanning..."))

    # Setup logger
    directory = os.path.dirname('logs/')
    if not os.path.exists(directory):
        os.makedirs(directory)
    logger = logging.getLogger(__name__)
    hdlr = logging.FileHandler('logs/' + datetime.now().strftime("%Y%m%d_%H%M") + '.log')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    # Header log file
    logger.info("Detected requests contain possibly dga-domains:")

    # For work time duration
    start_time = datetime.now()

    # Main process, scanning network
    sniff(iface=interface, filter="port 53",count=1, store=0, prn=packet_callback)

    stop_time = datetime.now()
    total_time = stop_time - start_time
    print("[*] Scan stopped")
    print("Scan duration: %s" % (total_time))
    logger.info("Scan duration: %s" % (total_time))

    if pred_result == 1:
        progress_queue.put((99, "Detected dga domain, blocking."))
        iptables(dga_hosts)
    else:
        progress_queue.put((99, "None detected"))

    time.sleep(2)
    iptables(dga_hosts)

#     answer = input("You want block possibly dangerous hosts? Enter yes or no: ")
#     if answer == "yes":
#         iptables(dga_hosts)
#     elif answer == "No":
#         print("Skipping blocking...")


if __name__ == "__main__":
    capture()
