"""SSL configuration for MongoDB Atlas connection on Windows."""
import ssl
import certifi


def create_ssl_context():
    """Create proper SSL context for MongoDB Atlas connection.

    This fixes the TLSV1_ALERT_INTERNAL_ERROR on Windows with OpenSSL 3.0+
    """
    # Create SSL context with proper settings for MongoDB Atlas
    ctx = ssl.create_default_context(cafile=certifi.where())

    # Set minimum TLS version to TLS 1.2 (MongoDB Atlas requirement)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    # Set maximum TLS version to TLS 1.3
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3

    # Enable all ciphers
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')

    # Check hostname and certificates
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    return ctx
