import simpy
import random
import numpy as np



arrival_times = [0]*9999999
start_times = [0]*9999999
finish_times = [0]*9999999
api_order_Q_times = [0]*99999
web_order_Q_times = [0]*99999
delivery_chat_Q_times = [0]*99999
api_rest_info_Q_times = [0]*99999
web_rest_info_Q_times = [0]*99999
delivery_req_Q_times = [0]*99999
order_check_Q_times = [0]*99999
api_order_expired = 0
api_order_all = 0
web_order_expired = 0
web_order_all = 0
delivery_chat_expired = 0
delivery_chat_all = 0
api_rest_info_expired = 0
api_rest_info_all = 0
web_rest_info_expired = 0
web_rest_info_all = 0
delivery_req_expired = 0
delivery_req_all = 0
order_check_expired = 0
order_check_all = 0
online_food = ''


class MonitoredResource(simpy.PriorityResource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue_lengths = []
        self.utilized_time = 0

    def request(self, *args, **kwargs):
        self.queue_lengths.append(len(self.queue))
        return super().request(*args, **kwargs)

    def release(self, *args, **kwargs):
        self.queue_lengths.append(len(self.queue))
        return super().release(*args, **kwargs)


class Online_food(object):
    def __init__(self, env, num_rest_mng, num_cust_mng, num_ord_mng, num_deliv_mng, num_pay_mng, num_api_mng, num_web_mng):
        self.env = env
        self.rest_mng = MonitoredResource(env, capacity = num_rest_mng)
        self.cust_mng = MonitoredResource(env, capacity = num_cust_mng)
        self.ord_mng = MonitoredResource(env, capacity = num_ord_mng)
        self.deliv_mng = MonitoredResource(env, capacity = num_deliv_mng)
        self.pay_mng = MonitoredResource(env, capacity = num_pay_mng)
        self.api_mng = MonitoredResource(env, capacity = num_api_mng)
        self.web_mng = MonitoredResource(env, capacity = num_web_mng)
    
    def restaurant_management(self, customer):
        service_time = np.random.exponential(scale=8)
        yield self.env.timeout(int(service_time)/60)
        print(f"Restaurant management finished for customer {customer} at {self.env.now:.2f}")

    def customer_management(self, customer):
        service_time = np.random.exponential(scale=5)
        yield self.env.timeout(int(service_time)/60)
        print(f"Customer management finished for customer {customer} at {self.env.now:.2f}")
    
    def order_management(self, customer):
        service_time = np.random.exponential(scale=6)
        yield self.env.timeout(int(service_time)/60)
        print(f"Order management finished for customer {customer} at {self.env.now:.2f}")

    def delivery_management(self, customer):
        service_time = np.random.exponential(scale=9)
        yield self.env.timeout(int(service_time)/60)
        print(f"Delivery management finished for customer {customer} at {self.env.now:.2f}")

    def payment_management(self, customer):
        service_time = np.random.exponential(scale=12)
        yield self.env.timeout(int(service_time)/60)
        print(f"Payment management finished for customer {customer} at {self.env.now:.2f}")
    
    def api_management(self, customer):
        service_time = np.random.exponential(scale=2)
        yield self.env.timeout(int(service_time)/60)
        print(f"API management finished for customer {customer} at {self.env.now:.2f}")

    def web_management(self, customer):
        service_time = np.random.exponential(scale=3)
        yield self.env.timeout(int(service_time)/60)
        print(f"Web management finished for customer {customer} at {self.env.now:.2f}")
    

# now we should define different user requests

def api_order(env, customer, online_food, max_wait):
    global api_order_expired, api_order_all
    api_order_all += 1
    arrival_times[customer] = env.now
    wait_time = 0
    temp = env.now
    with online_food.api_mng.request(priority=1) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            api_order_expired += 1
            return
        api_order_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.api_management(customer))
    online_food.api_mng.utilized_time += (env.now - temp2)

    temp = env.now
    with online_food.ord_mng.request(priority=1) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            api_order_expired += 1
            return
        api_order_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.order_management(customer))
    online_food.ord_mng.utilized_time += (env.now - temp2)

    temp = env.now
    with online_food.pay_mng.request(priority=1) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            api_order_expired += 1
            return
        api_order_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.payment_management(customer))
    online_food.pay_mng.utilized_time += (env.now - temp2)
    finish_times[customer] = env.now



def web_order(env, customer, online_food, max_wait):
    global web_order_expired, web_order_all
    web_order_all += 1
    arrival_times[customer] = env.now
    wait_time = 0
    temp = env.now
    with online_food.web_mng.request(priority=1) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            web_order_expired += 1
            return
        web_order_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.web_management(customer))
    online_food.web_mng.utilized_time += (env.now - temp2)

    temp = env.now
    with online_food.ord_mng.request(priority=1) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            web_order_expired += 1
            return
        web_order_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.order_management(customer))
    online_food.ord_mng.utilized_time += (env.now - temp2)

    temp = env.now
    with online_food.pay_mng.request(priority=1) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            web_order_expired += 1
            return
        web_order_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.payment_management(customer))
    online_food.pay_mng.utilized_time += (env.now - temp2)
    finish_times[customer] = env.now
    


def delivery_chat(env, customer, online_food, max_wait):
    global delivery_chat_expired, delivery_chat_all
    delivery_chat_all += 1
    arrival_times[customer] = env.now
    wait_time = 0
    temp = env.now
    with online_food.api_mng.request(priority=2) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            delivery_chat_expired += 1
            return
        delivery_chat_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.api_management(customer))
    online_food.api_mng.utilized_time += (env.now - temp2)

    temp = env.now
    with online_food.cust_mng.request(priority=2) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            delivery_chat_expired += 1
            return
        delivery_chat_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.customer_management(customer))
    online_food.cust_mng.utilized_time += (env.now - temp2)

    temp = env.now
    with online_food.deliv_mng.request(priority=2) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            delivery_chat_expired += 1
            return
        delivery_chat_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.delivery_management(customer))
    online_food.deliv_mng.utilized_time += (env.now - temp2)
    finish_times[customer] = env.now



def api_restaurant_info(env, customer, online_food, max_wait):
    global api_rest_info_expired, api_rest_info_all
    api_rest_info_all += 1
    arrival_times[customer] = env.now
    wait_time = 0
    temp = env.now
    with online_food.api_mng.request(priority=2) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            api_rest_info_expired += 1
            return
        api_rest_info_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.api_management(customer))
    online_food.api_mng.utilized_time += (env.now - temp2)

    temp = env.now
    with online_food.rest_mng.request(priority=2) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            api_rest_info_expired += 1
            return
        api_rest_info_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.restaurant_management(customer))
    online_food.rest_mng.utilized_time += (env.now - temp2)
    finish_times[customer] = env.now



def web_restaurant_info(env, customer, online_food, max_wait):
    global web_rest_info_expired, web_rest_info_all
    web_rest_info_all += 1
    arrival_times[customer] = env.now
    wait_time = 0
    temp = env.now
    with online_food.web_mng.request(priority=2) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            web_rest_info_expired += 1
            return
        web_rest_info_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.web_management(customer))
    online_food.web_mng.utilized_time += (env.now - temp2)

    temp = env.now
    with online_food.rest_mng.request(priority=2) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            web_rest_info_expired += 1
            return
        web_rest_info_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.restaurant_management(customer))
    online_food.rest_mng.utilized_time += (env.now - temp2)
    finish_times[customer] = env.now



def delivery_request(env, customer, online_food, max_wait):
    global delivery_req_expired, delivery_req_all
    delivery_req_all += 1
    arrival_times[customer] = env.now
    wait_time = 0
    temp = env.now
    with online_food.web_mng.request(priority=1) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            delivery_req_expired += 1
            return
        delivery_req_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.web_management(customer))
    online_food.web_mng.utilized_time += (env.now - temp2)

    temp = env.now
    with online_food.rest_mng.request(priority=1) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            delivery_req_expired += 1
            return
        delivery_req_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.restaurant_management(customer))
    online_food.rest_mng.utilized_time += (env.now - temp2)

    temp = env.now
    with online_food.deliv_mng.request(priority=1) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            delivery_req_expired += 1
            return
        delivery_req_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.delivery_management(customer))
    online_food.deliv_mng.utilized_time += (env.now - temp2)
    
    finish_times[customer] = env.now



def order_check(env, customer, online_food, max_wait):
    global order_check_expired, order_check_all
    order_check_all += 1
    arrival_times[customer] = env.now
    wait_time = 0
    temp = env.now
    with online_food.api_mng.request(priority=2) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            order_check_expired += 1
            return
        order_check_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.api_management(customer))
    online_food.api_mng.utilized_time += (env.now - temp2)

    temp = env.now
    with online_food.ord_mng.request(priority=2) as request:
        yield request
        temp2 = env.now
        wait_time += temp2 - temp
        if wait_time > max_wait:
            print(f"Customer {customer} timeout!")
            order_check_expired += 1
            return
        order_check_Q_times[customer] += (env.now - temp)
        yield env.process(online_food.order_management(customer))
    online_food.ord_mng.utilized_time += (env.now - temp2)
    finish_times[customer] = env.now





def run_online_food(env, num_rest_mng, num_cust_mng, num_ord_mng, num_deliv_mng, num_pay_mng, num_api_mng, num_web_mng, arrival_rate, max_wait_time):
    global online_food
    online_food = Online_food(env, num_rest_mng, num_cust_mng, num_ord_mng, num_deliv_mng, num_pay_mng, num_api_mng, num_web_mng)
    customer = 0
    while True:
        yield env.timeout(arrival_rate)  # Wait a bit before generating a new person

        customer += 1
        req_type = np.random.choice(np.arange(1, 8), p=[0.2, 0.1, 0.05, 0.25, 0.15, 0.2, 0.05])
        if req_type == 1:
            env.process(api_order(env, customer, online_food, max_wait_time[0]))
        elif req_type == 2:
            env.process(web_order(env, customer, online_food, max_wait_time[1]))
        elif req_type == 3:
            env.process(delivery_chat(env, customer, online_food, max_wait_time[2]))
        elif req_type == 4:
            env.process(api_restaurant_info(env, customer, online_food, max_wait_time[3]))
        elif req_type == 5:
            env.process(web_restaurant_info(env, customer, online_food, max_wait_time[4]))
        elif req_type == 6:
            env.process(delivery_request(env, customer, online_food, max_wait_time[5]))
        elif req_type == 7:
            env.process(order_check(env, customer, online_food, max_wait_time[6]))
    
 



def print_average_queue_len():
    global online_food
    print("\n========================Average Queue Lengths=============================")
    try:
        rest_mng_q = online_food.rest_mng.queue_lengths
        print(f"Average Queue Length of Restaurant management service is {sum(rest_mng_q)/len(rest_mng_q)}")
    except:
        print(f"Average Queue Length of Restaurant management service is zero")
    try:
        cust_mng_q = online_food.cust_mng.queue_lengths
        print(f"Average Queue Length of Customer management service is {sum(cust_mng_q)/len(cust_mng_q)}")
    except:
        print(f"Average Queue Length of Restaurant management service is zero")
    try:
        ord_mng_q = online_food.ord_mng.queue_lengths
        print(f"Average Queue Length of Order management service is {sum(ord_mng_q)/len(ord_mng_q)}")
    except:
        print(f"Average Queue Length of Order management service is zero")
    try:
        deliv_mng_q = online_food.deliv_mng.queue_lengths
        print(f"Average Queue Length of Delivery management service is {sum(deliv_mng_q)/len(deliv_mng_q)}")
    except:
        print(f"Average Queue Length of Delivery management service is zero")
    try:
        pay_mng_q = online_food.pay_mng.queue_lengths
        print(f"Average Queue Length of Payment management service is {sum(pay_mng_q)/len(pay_mng_q)}")
    except:
        print(f"Average Queue Length of Payment management service is zero")
    try:
        api_mng_q = online_food.api_mng.queue_lengths
        print(f"Average Queue Length of API management service is {sum(api_mng_q)/len(api_mng_q)}")
    except:
        print(f"Average Queue Length of API management service is zero")
    try:
        web_mng_q = online_food.web_mng.queue_lengths
        print(f"Average Queue Length of Web management service is {sum(web_mng_q)/len(web_mng_q)}")
    except:
        print(f"Average Queue Length of Web management service is zero")
    try:
        sum_elem = sum(rest_mng_q) + sum(cust_mng_q) + sum(ord_mng_q) + sum(deliv_mng_q) + sum(pay_mng_q) + sum(api_mng_q) + sum(web_mng_q)
        sum_len = len(rest_mng_q) + len(cust_mng_q) + len(ord_mng_q) + len(deliv_mng_q) + len(pay_mng_q) + len(api_mng_q) + len(web_mng_q)
        print(f"\nAverage Queue Length of all services is {sum_elem/sum_len}")
    except:
        print(f"\nAverage Queue Length of all services is zero")




def print_average_queue_time():
    global api_order_Q_times, delivery_chat_Q_times, web_order_Q_times, api_rest_info_Q_times, web_rest_info_Q_times, delivery_req_Q_times, order_check_Q_times
    print("\n========================Average Queue Times=============================")
    try:
        api_order_Q_times = list(filter(lambda x: x != 0, api_order_Q_times))
        print(f"Average Queue time of API orders is {sum(api_order_Q_times)/len(api_order_Q_times)}")
    except:
        print(f"Average Queue time of API orders is zero")
    try:
        web_order_Q_times = list(filter(lambda x: x != 0, web_order_Q_times))
        print(f"Average Queue time of Web orders is {sum(web_order_Q_times)/len(web_order_Q_times)}")
    except:
        print(f"Average Queue time of Web orders is zero")
    try:
        delivery_chat_Q_times = list(filter(lambda x: x != 0, delivery_chat_Q_times))
        print(f"Average Queue time of Delivery chat is {sum(delivery_chat_Q_times)/len(delivery_chat_Q_times)}")
    except:
        print(f"Average Queue time of Delivery chat is zero")
    try:
        api_rest_info_Q_times = list(filter(lambda x: x != 0, api_rest_info_Q_times))
        print(f"Average Queue time of checking restaurant info using API is {sum(api_rest_info_Q_times)/len(api_rest_info_Q_times)}")
    except:
        print(f"Average Queue time of checking restaurant info using API is zero")
    try:
        web_rest_info_Q_times = list(filter(lambda x: x != 0, web_rest_info_Q_times))
        print(f"Average Queue time checking restaurant info using Web is {sum(web_rest_info_Q_times)/len(web_rest_info_Q_times)}")
    except:
        print(f"Average Queue time checking restaurant info using Web is zero")
    try:
        delivery_req_Q_times = list(filter(lambda x: x != 0, delivery_req_Q_times))
        print(f"Average Queue time of requesting a delivery is {sum(delivery_req_Q_times)/len(delivery_req_Q_times)}")
    except:
        print(f"Average Queue time of requesting a delivery is zero")
    try:
        order_check_Q_times = list(filter(lambda x: x != 0, order_check_Q_times))
        print(f"Average Queue time of checking order is {sum(order_check_Q_times)/len(order_check_Q_times)}")
    except:
        print(f"Average Queue time of checking order is zero")
    try:
        sum_elem = sum(api_order_Q_times) + sum(web_order_Q_times) + sum(delivery_chat_Q_times) + sum(api_rest_info_Q_times) + sum(web_rest_info_Q_times) + sum(delivery_req_Q_times) + sum(order_check_Q_times)
        sum_len = len(api_order_Q_times) + len(web_order_Q_times) + len(delivery_chat_Q_times) + len(api_rest_info_Q_times) + len(web_rest_info_Q_times) + len(delivery_req_Q_times) + len(order_check_Q_times)
        print(f"\nAverage Queue time of all type of requests is {sum_elem/sum_len}")
    except:
        print(f"\nAverage Queue time of all services is zero")




def print_utilizations(simulation_time):
    global online_food
    print("\n========================Server Utilization=============================")
    u1 = online_food.rest_mng.utilized_time
    print(f"Utilization of Restaurant management service is {u1/simulation_time}")

    u2 = online_food.cust_mng.utilized_time
    print(f"Utilization of Customer management service is {u2/simulation_time}")

    u3 = online_food.ord_mng.utilized_time
    print(f"Utilization of Order management service is {u3/simulation_time}")

    u4 = online_food.deliv_mng.utilized_time
    print(f"Utilization of Delivery management service is {u4/simulation_time}")

    u5 = online_food.pay_mng.utilized_time
    print(f"Utilization of Payment management service is {u5/simulation_time}")

    u6 = online_food.api_mng.utilized_time
    print(f"Utilization of API management service is {u6/simulation_time}")

    u7 = online_food.web_mng.utilized_time
    print(f"Utilization of Web management service is {u7/simulation_time}")

    sum_utilized = u1 + u2 + u3 + u4 + u5+ u6 + u7
    print(f"\nUtilization of all services is {sum_utilized/simulation_time}\n")


def print_expired_percentage():
    global api_order_expired, delivery_chat_expired, web_order_expired, api_rest_info_expired, web_rest_info_expired, delivery_req_expired, order_check_expired
    global api_order_all, delivery_chat_all, web_order_all, api_rest_info_all, web_rest_info_all, delivery_req_all, order_check_all
    print("\n========================Timeout Requests=============================")
    try:
        print(f"Timeout Percentage of API orders is {api_order_expired/api_order_all}")
    except:
        pass
    try:
        print(f"Timeout Percentage of Web orders is {web_order_expired/web_order_all}")
    except:
        pass
    try:
        print(f"ATimeout Percentage of Delivery chat is {delivery_chat_expired/delivery_chat_all}")
    except:
        pass
    try:
        print(f"Timeout Percentage of checking restaurant info using API is {api_rest_info_expired/api_rest_info_all}")
    except:
        pass
    try:
        print(f"Timeout Percentage of checking restaurant info using Web is {web_rest_info_expired/web_rest_info_all}")
    except:
        pass
    try:
        print(f"Timeout Percentage of requesting a delivery is {delivery_req_expired/delivery_req_all}")
    except:
        pass
    try:
        print(f"Timeout Percentage of checking order is {order_check_expired/order_check_all}")
    except:
        pass
    try:
        sum_elem = api_order_expired+delivery_chat_expired+web_order_expired+api_rest_info_expired+web_rest_info_expired+delivery_req_expired+order_check_expired
        sum_len = api_order_all+ delivery_chat_all+ web_order_all+ api_rest_info_all+web_rest_info_all+delivery_req_all+order_check_all
        print(f"\nTimeout Percentage of all type of requests is {sum_elem/sum_len}")
    except:
        print(f"\nTimeout Percentage of all services is zero")





def main():
    
    random.seed(42)
    num_rest_mng, num_cust_mng, num_ord_mng, num_deliv_mng, num_pay_mng, num_api_mng, num_web_mng = list(map(int, input().strip().split()))
    arrival_rate = float(input())
    arrival_rate = 1 / arrival_rate
    arrival_rate /= 60
    simulation_time = int(input())/60
    max_wait_time = list(map(int, input().strip().split()))
    # Run the simulation
    env = simpy.Environment()
    env.process(run_online_food(env, num_rest_mng, num_cust_mng, num_ord_mng, num_deliv_mng, num_pay_mng, num_api_mng, num_web_mng, arrival_rate, max_wait_time))
    env.run(simulation_time)

    print_average_queue_len()
    print_average_queue_time()
    print_utilizations(simulation_time)
    print_expired_percentage()


if __name__ == "__main__":
    main()             