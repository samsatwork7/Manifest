TAKEOVER_FINGERPRINTS = {
    "github.io": "GitHub Pages",
    "herokudns.com": "Heroku",
    "amazonaws.com": "AWS S3",
    "cloudfront.net": "CloudFront",
    "azurewebsites.net": "Azure",
}

class TakeoverScanner:

    def detect(self, cname):
        for sig, service in TAKEOVER_FINGERPRINTS.items():
            if sig in cname:
                return service
        return None
