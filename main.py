import tornado.ioloop
import tornado.web

import uuid
import os

import base64

TEMP_PATH="tmp/"
def get_random_name():
    uuid_str = uuid.uuid4().hex
    return uuid_str

def remove_tmp_file(filename):
    filename=filename.split(".")[0]
    exts=[".v",".ys",".dot",".jpeg"]
    for i in exts:
        try:
            os.remove(TEMP_PATH+filename+i)
        except:
            print("wow,the file is not exist! filename:%s" % filename+i)
    

def produce_rtl_image(filename,language,template,top_name="top_module"):
    filename_without_ext=filename.split(".")[0]

    ## 替换模板，生成正确的ys文件，供yosys调用
    newscript_text=template.replace("FILENAME",TEMP_PATH+filename)
    newscript_text=newscript_text.replace("TOPMODULE_NAME",top_name)
    newscript_text=newscript_text.replace("FILE_WITHOUT_EXT",TEMP_PATH+filename_without_ext) 
    if(language=="verilog"):
        newscript_text=newscript_text.replace("LANGUAGE","sv") 
    else:
        newscript_text=newscript_text.replace("LANGUAGE","vhdl")  

    newscript_filename=filename_without_ext+".ys"
    with open(TEMP_PATH+newscript_filename,"w+") as f:
        f.write(newscript_text)
    
    if(os.system("yosys "+TEMP_PATH+newscript_filename)!=0):
        #remove_tmp_file(filename_without_ext)
        return None


    jpgfilename=TEMP_PATH+filename_without_ext+".jpeg"
    b64result=""
    with open(jpgfilename,"rb") as f:
        b64result=base64.b64encode(f.read())
    return b64result
    

def read_ys_template():
    global GATE_template
    global RTL_template
    with open("GATE_script.ys","r") as f:
        GATE_template=f.read()
    with open("RTL_script.ys","r") as f:
        RTL_template=f.read()
    

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class GetHDLHandler(tornado.web.RequestHandler):
    def post(self):
        text=self.get_body_argument("hdl_text")
        language=self.get_body_argument("language")
        level=self.get_body_argument("level")
        top_module=self.get_body_argument("top_module_name")

        filename=get_random_name() +".v"

        if(level=="rtl"):
            template=RTL_template
        else:
            template=GATE_template
        
        with open(TEMP_PATH+filename,"w+") as f:
            f.write(text)
        imgb64_code=produce_rtl_image(filename,language,template,top_module)
        self.render("image.html",img_b64=imgb64_code)
        #remove_tmp_file(filename)

        

if __name__=="__main__":
    app=tornado.web.Application([(r"/",MainHandler),(r"/hdl",GetHDLHandler)])
    read_ys_template()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

