import nfc.clf
import logging
import passport
from nfc.dep import Initiator

# Uncomment this if you want to see more stuff!
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
#logging.getLogger("nfc.clf").setLevel(logging.DEBUG)
#logging.getLogger("nfc.dep").setLevel(logging.DEBUG)

def probe_badge():
    r = nfc.clf.ContactlessFrontend()
    try: 
        r.open('tty:ACM0:pn532')
    except:
        r.open('tty:ACM1:pn532')

    try:
        dep = Initiator(r)

        # Use brs to force 106a because this does not seem to process the atr_res correctly
        dep.activate(brs=0)
        # dep.activate(target = {"brty": "106A"}, brs=0)

        print("Activation done !")
        # print(f"{dep}")

        mem = bytearray()

        for i in range(0, 0x400//64):
            print(f"Dumping page {i}")

            req = b'\x01' + i.to_bytes(1)
            res = dep.exchange(req, 0.1)
            print(res)

            mem.extend(res)

        state = passport.parse_flash(mem)
        print(state)


        # Things that we need to return:
        # State
        # Calculated Score + Receipt

        receipt = passport.receipt_from_flash(mem)

        # Here we can add additional items to the receipt if wanted
        # For example:
        # receipt.add_line("Extra 10 points", 10)

        score = receipt.total()

        req = b'\x02' + passport.serialize_score(score)
        dep.exchange(req, 0.1)

        return (state, score, receipt.as_string())

    finally:
        r.close()

if __name__=="__main__":
    while True:
        try:
            print("PRESENT PASSPORT!")
            (state, score, receipt) = probe_badge()
            break
        except:
            print("Passport not found... Trying again \n")

    print(receipt)
