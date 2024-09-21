This is the source code for a minimal GCP Cloud Run function wrapping
[ansifier](https://github.com/amminer/ansifier)

I'm planning on making an actual decent front-end and opening up some of the switches that ansifier
accepts soon, for now I'm just focusing on getting the back end of things set up how I want it.

# Usage

Visit https://ansifier.com/ in a browser for a simple HTML/JS UI.

You can also use the function programatically by sending an application/json HTTP request with
fields for "imageURL" and "format". More (optional) fields soon!

Please don't eat all my free GCP credits :)
