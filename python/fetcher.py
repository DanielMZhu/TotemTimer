import ssl
import circuitpython_base64 as base64
import wifi
import socketpool
import adafruit_requests
import gc
class Fetcher():
    
    def __init__(self):
        username = "daniel"
        password = "deenodurl69A"
        self.wifi_name = "Verizon_3NY9X3"
        self.wifi_pass = "tron4-reed-elk"
        wifi.radio.connect(self.wifi_name, self.wifi_pass)
        pool = socketpool.SocketPool(wifi.radio)
        self.requests = adafruit_requests.Session(pool, ssl.create_default_context())
        self.url = "https://courtsquare.pythonanywhere.com/api/data"
        
        auth_string = f"{username}:{password}"
        auth_bytes = auth_string.encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")

        # Create the headers with the Authorization field for Basic Auth
        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json"
        }
        gc.collect()
        
    def get_times(self):
        try:
            response = self.requests.get(self.url, headers=self.headers)
            json = response.json()
            response.close()
            e = json["e_line"]["south"]
            if e > 999999:
                e = "n/a"
            else:
                e = str(e//60)+"m"
            
            m = json["m_line"]["south"]
            if m > 99999:
                m = "n/a"
            else:
                m = str(m//60)+"m"
            
            svn = json["7_line"]
            svn_n = svn["north"]
            svn_s = svn["south"]
            
            if svn_n > 99999:
                svn_n = "n/a"
            else:
                svn_n = str(svn_n//60)+"m"
                
            if svn_s > 99999:
                svn_s = "n/a"
            else:
                svn_s = str(svn_s//60)+"m"
            return e, m, svn_s, svn_n
        except Exception as e:
            print("huh???",e)
            return "err", "err", "err", "err"
        
        
    