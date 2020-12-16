import scrapy
from ecommerce.items import EcommerceItem


class GmarketCateAllSpider(scrapy.Spider):
    name = 'gmarket_cate_all'

    def start_requests(self):
        yield scrapy.Request(url='http://corners.gmarket.co.kr/Bestsellers/',callback=self.parse_mainpages)
       
    def parse_mainpages(self, response):
        category_names = response.css('div.gbest-cate ul.by-group li a::text').getall()
        category_links = response.css('div.gbest-cate ul.by-group li a::attr(href)').getall()
        
        # 1st category crawling
        for index,category_link in enumerate(category_links) :
            yield scrapy.Request(url='http://corners.gmarket.co.kr'+category_link,
                                callback=self.parse_maincategory,
                                meta={'maincategory_name' :category_names[index],'subcategory_name':'ALL'})
        # 2nd category crawling
        for index,category_link in enumerate(category_links) :
            yield scrapy.Request(url='http://corners.gmarket.co.kr'+category_link,
                                callback=self.parse_subcategory,
                                meta={'maincategory_name' :category_names[index]})
    
    def parse_subcategory(self,response) :
        print('parse_subcategory',response.meta['maincategory_name'])
        subcategory_names = response.css('div.navi.group > ul > li > a::text').getall()
        subcategory_links = response.css('div.navi.group > ul > li > a::attr(href)').getall()
        for index,subcategory_link in enumerate(subcategory_links) :
            yield scrapy.Request(url='http://corners.gmarket.co.kr'+subcategory_link,
                                callback=self.parse_maincategory,
                                meta={
                                    'maincategory_name':response.meta['maincategory_name'],
                                    'subcategory_name':subcategory_names[index]
                                    })

    def parse_maincategory(self,response) :
        print('parse_maincategory',response.meta['maincategory_name'],response.meta['subcategory_name'])

        best_items = response.css('div.best-list')[1]
        for index,best_item in enumerate(best_items.css('li')) :
            doc = EcommerceItem()
            ranking = index + 1
            title = best_item.css('a.itemname::text').get()
            ori_price = best_item.css('div.o-price::text').get()
            dis_price = best_item.css('div.s-price strong span span::text').get()
            discount_percent = best_item.css('div.s-price em::text').get()
            
            
            if ori_price is None :
                ori_price = dis_price
            # ori_price = ori_price.replace('원','')
            # dis_price = dis_price.replace('원','')
            if discount_percent is None :
                discount_percent = 0
            else :
                discount_percent = discount_percent.replace('%','')
            
            doc['maincategory_name'] = response.meta['maincategory_name']
            doc['subcategory_name'] = response.meta['subcategory_name']
            doc['ranking'] = ranking
            doc['title'] = title
            doc['ori_price'] = ori_price
            doc['dis_price'] = dis_price
            doc['discount_percent'] = discount_percent

            yield doc
