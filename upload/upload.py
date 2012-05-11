#! /usr/bin/env python

import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path
from tornado.options import define, options
import Image
import os

define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        settings = {
                "static_path": os.path.join(os.path.dirname(__file__), "static"),
                "template_path":".",
                "debug":True,
                }

        handlers = [
            (r"/", HomeHandler),
            (r"/upload", UploadHandler),
            (r"/(images/close\.png)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
            (r"/(images/loading\.gif)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
        ]
        self.img_list = []
        tornado.web.Application.__init__(self, handlers, **settings)
        
class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("t.html", img_list=self.application.img_list)
        
class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        file1 = self.request.files['file1'][0]
        # now you can do what you want with the data, we will just save the file to an uploads folder
        upload_path = 'static/uploads'
        filename = file1['filename']
        output_file = open(os.path.join(upload_path, filename), 'w')
        output_file.write(file1['body'])
        output_file.close()

        name,ext = os.path.splitext(filename)
        thumb = name+"-thumb"+ext
        print thumb
        im = Image.open(os.path.join(upload_path, filename))
        print im.size
        if im.size[0] > 150 or im.size[1] > 150:
            if max(im.size[0], im.size[1]) == im.size[0]:
                w = 150
                h = int(im.size[1] * float(w) / im.size[0])
            else:
                h = 150
                w = int(im.size[0] * float(h) / im.size[1])
            print w, h
            im.thumbnail((w,h))
            im.save(os.path.join(upload_path, thumb))
            self.application.img_list.append((os.path.join(upload_path, filename), os.path.join(upload_path, thumb)))
        else:
            self.application.img_list.append((os.path.join(upload_path, filename), os.path.join(upload_path, filename)))
        del im
        self.redirect('/')

        
def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == "__main__":
    main()

