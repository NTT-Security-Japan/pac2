import sys
from pypowerautomate.package import Package


sys.path.append("./pac2") # workaround for import error

from uuid import uuid4
from  pac2.app.flow.beacon import HTTPBeacon


DUMMY_FLOWMANAGEMENT_ID = "00000000000000000000000000000000"
DUMMY_PAC2_URL = "http://dummy.pac2.localhost:9999/"

def main():
    print(str(uuid4()))
    beacon = HTTPBeacon(DUMMY_FLOWMANAGEMENT_ID,str(uuid4()),DUMMY_PAC2_URL)
    Package("dummy_http_beacon",beacon.generate_flow()).export_zipfile()

if __name__ == "__main__":
    main()
