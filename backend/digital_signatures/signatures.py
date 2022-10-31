import OpenSSL
import os
import time
import argparse
from pyhanko.sign.general import load_cert_from_pemder
from pyhanko_certvalidator import ValidationContext
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from PDFNetPython3.PDFNetPython import *
from typing import Tuple
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers, timestamps, fields
from pyhanko.sign.fields import *
from pyhanko_certvalidator import ValidationContext
from pyhanko import stamp
from pyhanko.pdf_utils import text
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers

def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + "_" + str(counter) + extension
        counter += 1

    return path

def createKeyPair(type, bits):
    """
    Create a public/private key pair
    Arguments: Type - Key Type, must be one of TYPE_RSA and TYPE_DSA
               bits - Number of bits to use in the key (1024 or 2048 or 4096)
    Returns: The public/private key pair in a PKey object
    """
    pkey = OpenSSL.crypto.PKey()
    pkey.generate_key(type, bits)
    return pkey



def create_self_signed_cert(pKey, signer_name):
    """Create a self signed certificate. This certificate will not require to be signed by a Certificate Authority."""
    # Create a self signed certificate
    cert = OpenSSL.crypto.X509()
    # Common Name (e.g. server FQDN or Your Name)
    cert.get_subject().CN = signer_name

    # Serial Number
    cert.set_serial_number(int(time.time() * 10))
    # Not Before
    cert.gmtime_adj_notBefore(0)  # Not before
    # Not After (Expire after 10 years)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    # Identify issue
    cert.set_issuer((cert.get_subject()))
    cert.set_pubkey(pKey)
    cert.sign(pKey, 'sha256')  # or cert.sign(pKey, 'sha256')
    return cert


def load(signer_name):
    """Generate the certificate"""
    summary = {}
    summary['OpenSSL Version'] = OpenSSL.__version__
    # Generating a Private Key...
    key = createKeyPair(OpenSSL.crypto.TYPE_RSA, 1024)
    # PEM encoded
    # create path at user-certificates
    #priv_key_path = os.path.join('user-certificates', signer_name + '_private_key.pem')
    priv_key_path = os.path.join(signer_name + '_private_key.pem')
    priv_key_path = uniquify(priv_key_path)

    with open(priv_key_path, 'wb') as pk:
        pk_str = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)
        pk.write(pk_str)
        summary['Private Key'] = pk_str
    # Done - Generating a private key...
    # Generating a self-signed client certification...
    cert = create_self_signed_cert(pKey=key,signer_name=signer_name)
    #certificate_path = os.path.join('user-certificates', signer_name + '_certificate.pem')
    certificate_path = os.path.join(signer_name + '_certificate.pem')
    certificate_path = uniquify(certificate_path)
    with open(certificate_path, 'wb') as cer:
        cer_str = OpenSSL.crypto.dump_certificate(
            OpenSSL.crypto.FILETYPE_PEM, cert)
        cer.write(cer_str)
        summary['Self Signed Certificate'] = cer_str
    # Done - Generating a self-signed client certification...
    # Generating the public key...

    # with open('public_key.pem', 'wb') as pub_key:
    #     pub_key_str = OpenSSL.crypto.dump_publickey(
    #         OpenSSL.crypto.FILETYPE_PEM, cert.get_pubkey())
    #     #print("Public key = ",pub_key_str)
    #     pub_key.write(pub_key_str)
    #     summary['Public Key'] = pub_key_str
    # Done - Generating the public key...
    
    # Take a private key and a certificate and combine them into a PKCS12 file.
    # Generating a container file of the private key and the certificate...
    
    # You may convert a PKSC12 file (.pfx) to a PEM format
    # Done - Generating a container file of the private key and the certificate...
    # To Display A Summary
    # print("## Initialization Summary ##################################################")
    # print("\n".join("{}:{}".format(i, j) for i, j in summary.items()))
    # print("############################################################################")
    return certificate_path, priv_key_path

def sign_pdf(pdf_path,certificate_path, private_key_path):
    signer = signers.SimpleSigner.load(
    private_key_path, certificate_path,)

    with open(pdf_path, 'rb') as inf:
        w = IncrementalPdfFileWriter(inf)
        fields.append_signature_field(
            w, sig_field_spec=fields.SigFieldSpec(
                'Signature', box=(200, 600, 400, 660)
            )
        )

        meta = signers.PdfSignatureMetadata(field_name='Signature')
        pdf_signer = signers.PdfSigner(
            meta, signer=signer
           
        )
        with open(os.path.splitext(pdf_path)[0]+'_signed'+os.path.splitext(pdf_path)[1], 'wb') as outf:
            pdf_signer.sign_pdf(w, output=outf)
    
    # delete the private key
    os.remove(private_key_path)
    # replace the original pdf with the signed pdf
    os.remove(pdf_path)
    os.rename(os.path.splitext(pdf_path)[0]+'_signed'+os.path.splitext(pdf_path)[1], pdf_path)
    
    return pdf_path

def verify_pdf(certificate_path, pdf_path):
    root_cert = load_cert_from_pemder(certificate_path)
    vc = ValidationContext(trust_roots=[root_cert])
    with open(pdf_path, 'rb') as doc:
        r = PdfFileReader(doc)
        try:
         sig = r.embedded_signatures[0]
         status = validate_pdf_signature(sig, vc)
         #print(status.pretty_print_details())
         output=str(status.pretty_print_details())
         if "The signature is cryptographically sound" in output:
            return True
       
        except:
            return False

# if __name__ == '__main__':
#     signer_name = 'test'
#     certificate_path, private_key_path = load(signer_name)
#     pdf_path = 'input.pdf'
#     pdf_path_signed = sign_pdf(pdf_path, certificate_path, private_key_path)
#     print(verify_pdf(certificate_path, pdf_path_signed))