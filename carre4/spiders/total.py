# -*- coding: utf-8 -*-
import scrapy
import requests
from bs4 import BeautifulSoup
import json 

class TotalSpider(scrapy.Spider):
	name = 'total'
	allowed_domains = ['supermercado.carrefour.com.ar']
	start_urls = ['http://supermercado.carrefour.com.ar/']
	pag = 1
	def start_requests(self):
		url ='https://supermercado.carrefour.com.ar/'
		yield scrapy.Request(url=url, callback=self.pasoUno)
	
	def pasoUno(self,response):
		resUno = response.xpath('//*[@id="level0-wrapper-"]/a/@href').extract()
		for x in resUno:
			yield scrapy.Request(url=x, callback=self.pasoDos)

	def pasoDos(self,response):
		sopa = BeautifulSoup(response.body,'lxml')
		categorias = [x.attrs for x in sopa.findAll('li')]
		for x in categorias:
			try:
				#print (x['class'])
				if 'category' in x['class'][0]:
					#cats.append(x['class'][0])
					cat = x['class'][0]
					urlc = 'https://supermercado.carrefour.com.ar/infinitescroll/ajax/category/?id={}'.format(cat[-4:].strip())
					yield scrapy.Request(url=urlc, callback=self.pasoTres)
			except:
				pass
	
	def pasoTres(self,response):
		
		urlf = response.url
		busca =  urlf+'&p={}'.format(self.pag)
		print('va a pasar a paso Cuarto lo siguiente {}'.format(urlf))
		yield scrapy.Request(url=urlf, meta={'page':self.pag}, callback=self.parse)
		
	
	def pasoCuatro(self,response, page=0):
		rjson = json.loads(response.body)
		final = rjson['content']['last']
		print(final)
		print('va a pasar este url a la funcion Parse: {}'.format(response.url))
		newurl = response.url
		if final == False:
			next_page_link = previouslink + 1 
			print(next_page)
			return scrapy.Request(url=self.urlf+'&p={}'.format(next_page), callback=self.parse)
			
		else:
			print('Llego a la ultima pagina')
			

	def parse(self, response):
		print('Llegó a la funcion Parse {}'.format(response.url))
		data = json.loads(response.text)
		inner = BeautifulSoup(data['content']['block'],'lxml')
		#for a in inner.findAll('p'):
		#	print (a.attrs)
		precios = [x.text.strip() for x in inner.findAll('p',{'class':'price'})]
		marca = [x.text.strip() for x in inner.findAll('p',{'class':'brand'})]
		producto = [x.text.strip() for x in inner.findAll('p',{'class':'title'})]
		eans= [x['src'].split('/')[-1].split("_")[0]for x in inner.findAll('img')]
		cats = inner.findAll('div',{'class':'producto-info'})
		cats =[cat['data-categorytext'] for cat in cats]
		for y in range(len(precios)):
			print(precios[y],marca[y],producto[y])
			yield  {'precio': precios[y].split('/n')[0], 'marca':marca[y], 'producto':producto[y],'Ean':eans[y], 'Url':response.url, 'Categ':cats[y]}