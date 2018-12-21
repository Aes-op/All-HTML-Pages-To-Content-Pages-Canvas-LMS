import requests
import urllib.request as req
from bs4 import BeautifulSoup


def testToken(token):
    accounts = requests.get(url + '/api/v1/course_accounts', params={'access_token': token})
    return accounts.json()


def tokenLogin():
    while True:
        accessToken = input('Please enter your Canvas API Access Token: ')
        test = testToken(accessToken)
        if 'errors' not in test:
            return accessToken
        else:
            print('Error: Invalid input, this may be due to an incorrect URL.\n')


def urlSelection():
    urlChoice = ("https://" + input("Please enter a URL for your Canvas instance. "
                                    "The format required is 'website.domainsuffix'. 'https://' will be"
                                    " appended to your input: "))
    return urlChoice


def courseSelection():
    while True:
        targetID = input("Please enter the target Course ID: ")
        print('\n')
        courseRequest = requests.get(url + "/api/v1/courses/{}".format(targetID), params={'access_token': token})
        course = courseRequest.json()
        if 'errors' not in course:
            print("You have selected the course \'{}\' \n".format(course['name']))
            courseChoice = input("Is this the correct course? Enter \'y\' for yes or \'n\' for no: ")
            print('\n')
            if courseChoice == "y":
                return targetID
            else:
                print("Restarting course selection. \n")
        else:
            print("Error: Course does not exist, or entered Course ID is invalid")


def getFullListOfModules():
    fullList = []
    modulesRequest = requests.get(url + "/api/v1/courses/{}/modules".format(courseID), params={'include[]': 'items',
                                                                                               'per_page': 100,
                                                                                               'access_token': token})
    modules = modulesRequest.json()
    for module in modules:
        fullList.append(module)
    while modulesRequest.links['current']['url'] != modulesRequest.links['last']['url']:
        modulesRequest = requests.get(modulesRequest.links['next']['url'], params={'include[]': 'items',
                                                                                   'per_page': 100,
                                                                                   'access_token': token})
        modules = modulesRequest.json()
        for module in modules:
            fullList.append(module)
    return fullList


def getFullListOfFiles():
    fullList = []
    itemsRequest = requests.get(url + "/api/v1/courses/{}/files".format(courseID), params={'include[]': 'items',
                                                                                               'per_page': 100,
                                                                                               'access_token': token})
    items = itemsRequest.json()
    for item in items:
        fullList.append(item)
    while itemsRequest.links['current']['url'] != itemsRequest.links['last']['url']:
        itemsRequest = requests.get(itemsRequest.links['next']['url'], params={'include[]': 'items',
                                                                                   'per_page': 100,
                                                                                   'access_token': token})
        items = itemsRequest.json()
        for item in items:
            fullList.append(item)
    return fullList


def getListOfModuleItems(module):
    itemsList = module['items']
    return itemsList


def getHTMLContent(fileURL):
    extractedContent = req.urlopen(fileURL)
    htmlContent = extractedContent.read()
    extractedContent.close()
    soup = BeautifulSoup(htmlContent, 'html.parser')
    head = soup.find('head')
    if head:
        head.extract()
    body = str(soup)
    return body


def convertAndDeleteNonLinkedHTMLFiles():
    print('***Converting non-linked HTML files.***\n')
    fullFilesList = getFullListOfFiles()
    htmlFilesList = []
    for file in fullFilesList:
        if file['content-type'] == 'text/html':
            htmlFilesList.append(file)
    percentage = float(100/len(htmlFilesList))
    percentageDone = float(0)
    for htmlFile in htmlFilesList:
        title = htmlFile['filename'].replace('.html', '').replace('.htm', '').replace('+', ' ')
        contentBody = getHTMLContent(htmlFile['url'])
        requests.post(url + "/api/v1/courses/{}/pages".format(courseID), params={'wiki_page[title]': title,
                                                                                 'wiki_page[body]': contentBody,
                                                                                 'wiki_page[editing_roles]': 'teachers',
                                                                                 'wiki_page[published]': 'true',
                                                                                 'access_token': token})
        requests.delete(url + "/api/v1/files/{}".format(htmlFile['id']), params={'access_token': token})
        percentageDone += percentage
        print(str("{:3.2f}".format(percentageDone)) + "% Complete!\n")
    return


def convertAndDeleteLinkedHTMLPages():
    print("***Converting linked HTML files.***\n")
    listOfModules = getFullListOfModules()
    for module in listOfModules:
        listOfModuleItems = getListOfModuleItems(module)
        for item in listOfModuleItems:
            if item['type'] == 'File':
                possibleHTML = requests.get(item['url'], params={'access_token': token}).json()
                if possibleHTML['content-type'] == 'text/html':
                    title = item['title'].replace('.html', '').replace('.htm', '')
                    contentBody = getHTMLContent(possibleHTML['url'])
                    postedPage = requests.post(url + "/api/v1/courses/{}/pages".format(courseID),
                                               params={'wiki_page[title]': title, 'wiki_page[body]': contentBody,
                                               'wiki_page[editing_roles]': 'teachers', 'wiki_page[published]': 'true',
                                               'access_token': token}).json()
                    requests.post(url + "/api/v1/courses/{}/modules/{}/items".format(courseID, module['id']),
                                  params={'module_item[title]': title, 'module_item[type]': 'Page',
                                          'module_item[position]': item['position'],
                                          'module_item[indent]': item['indent'],
                                          'module_item[page_url]': postedPage['url'],
                                          'access_token': token})
                    requests.delete(url + "/api/v1/files/{}".format(possibleHTML['id']), params={'access_token': token})
                    requests.delete(url + "/api/v1/courses/{}/modules/{}/items/{}".format(courseID, module['id'],
                                                                                          item['id']),
                                    params={'access_token': token})
                    print('{}'.format(title) + " has been converted.\n")
    return


url = urlSelection()
token = tokenLogin()
courseID = courseSelection()
convertAndDeleteLinkedHTMLPages()
convertAndDeleteNonLinkedHTMLFiles()
print("All HTML files converted.")
