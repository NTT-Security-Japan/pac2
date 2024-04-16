import sys
from pypowerautomate.package import Package


sys.path.append("./pac2") # workaround for import error

from uuid import uuid4
from  pac2.app.flow.beacon import DropboxBeacon

DUMMY_FLOWMANAGEMENT_ID = "00000000000000000000000000000000"
DUMMY_DROPBOX_ID = "11111111111111111111111111111111"

def main():
    print(str(uuid4()))
    beacon = DropboxBeacon(DUMMY_FLOWMANAGEMENT_ID,str(uuid4()),DUMMY_DROPBOX_ID)
    Package("dummy_dropbox_beacon",beacon.generate_flow()).export_zipfile()

if __name__ == "__main__":
    main()
