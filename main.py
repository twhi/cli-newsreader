from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import textwrap


class InputError(Exception):
    pass


def initialise_selenium():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('log-level=3')
    return webdriver.Chrome(options=chrome_options)


def get_top_10():
    top_10 = []
    t_10 = d.find_elements_by_xpath(TOP_10_XPATH)
    for t in t_10:
        top_10.append({
            'title': t.get_attribute("textContent").replace('\n', '').strip(),
            'link': t.get_attribute('href')
        })
    return top_10


def get_sections():
    sections = []
    sections.append({
        'title': 'Overall',
        'link': HOMEPAGE,
    })
    secs = d.find_elements_by_xpath(SECTIONS_XPATH)
    for s in secs:
        sections.append({
            'title': s.get_attribute("textContent").strip('\n'),
            'link': s.find_element_by_tag_name('a').get_attribute('href')
        })
    return sections


def input_integer(message, max_val):
    # keep prompting user until a valid input is made
    while True:
        try:
            selection = int(input(message))

            # if the input is within the allowed menu values then return this
            if int(selection) in MENU_OPTIONS.values():
                return selection
                break

            # if the input is too large then throw InputError
            if selection > max_val - 1:
                raise InputError
        except ValueError:
            # catches non int values
            print("Selection must be an integer, try again...")
            continue
        except InputError:
            # catches inputs that don't exist
            print("Invalid selection, please try again...")
            continue
        else:
            return selection
            break


def print_article():
    # print headline
    print('---------------------')
    print(textwrap.fill(d.find_element_by_xpath(HEADLINE_XPATH).text, MAX_TEXT_WIDTH))

    # print tagline
    print('---------------------')
    print(textwrap.fill(d.find_element_by_xpath(TAGLINE_XPATH).text, MAX_TEXT_WIDTH))

    # print article body
    print('---------------------')
    body = d.find_elements_by_xpath(ARTICLE_BODY_XPATH)
    for p in body:
        if not any(disallowed in p.text for disallowed in DISALLOWED_TEXT):
            if len(p.text) > 0:
                print(textwrap.fill(p.text, MAX_TEXT_WIDTH))
                print('\n')

    print('--- End of Article ---')


def print_top_10_articles(top_10, cat):
    print('\n########################')
    print('Top 10 {} articles:'.format(cat))
    for i, t in enumerate(top_10):
        print('[', i, '] - ', t['title'], sep='')


def print_categories(sec):
    print('\n########################\n')
    for i, s in enumerate(sec):
        print('[', i, '] - ', s['title'], sep='')
    print('\n[99] - Exit Program')


# initialise variables
HOMEPAGE = 'https://www.theguardian.com/uk'
SECTIONS_XPATH = '//header//ul[contains(@class, "subnav__list")]//li'
TOP_10_XPATH = '//div[@id="tabs-popular-1"]//a[contains(@class, "js-headline-text")]'
HEADLINE_XPATH = '//h1[contains(@class, "content__headline")]'
TAGLINE_XPATH = '//div[contains(@class, "content__standfirst")]'
ARTICLE_BODY_XPATH = '//div[contains(@class, "content__article-body")]//p'
MAX_TEXT_WIDTH = 70
MENU_OPTIONS = {
    'Back to Categories': 98,
    'Exit Program': 99,
}

DISALLOWED_TEXT = [
    'we have a small favour to ask.',
    'The Guardian will engage with the most critical issues of our time',
    'Our editorial independence means we set our own agenda',
    'We hope you will consider supporting us today.',
    'the Guardian will not stay quiet. This is our pledge',
    'We chose a different approach:',
    'Our editorial independence means we are free to investigate and challenge',
    'The Guardian believes that the problems we face on the climate crisis',
    'that will define the next decase, so delivering truthful reporting has never been more critical',
    'More people, like you, are reading and supporting the Guardian\'s',
    'we hope you will consider supporting our independent journalism today',
    'With a new Conservative government posed for office',
    'More people, like you, are reading and supporting',
    'will the 2020s offer more hope? This has been a turbulent',
    'More people than ever before are reading and supporting our journalism',
    'We have upheld our editorial independence in the face of',
    'None of this would have been attainable without our readers\' generosity',
    'As we enter a new decade, we need your support so we can keep delivering',
]

if __name__ == '__main__':

    # go to homepage and get top 10 articles
    d = initialise_selenium()
    d.get(HOMEPAGE)

    categories = get_sections()

    top_10_all = {}
    for s in categories:
        top_10_all[s['title']] = None

    # start reading loop
    back_to_categories = True
    while True:

        # prompt user to select category
        if back_to_categories:
            print_categories(categories)
            selection = input_integer('\nSelect a category: ', len(categories))
            if selection == 99:
                break
            category = categories[int(selection)]['title']
            print('Getting top {} articles...'.format(category))
            back_to_categories = False

        # get top 10 articles for selected category and display them
        if not top_10_all[category]:
            d.get(categories[int(selection)]['link'])
            t_10 = get_top_10()
            top_10_all[category] = t_10
        else:
            t_10 = top_10_all[category]

        # print out the top 10 along with the other menu options
        print_top_10_articles(t_10, category)
        print('\n')
        for k, v in MENU_OPTIONS.items():
            print('[{0}] - {1}'.format(v, k))

        # prompt user to select an article
        selection = input_integer('\nSelect an article to read: ', len(t_10))

        # catch menu options - if none were selected, then get the article and print it
        if selection == 98:
            back_to_categories = True
        elif selection == 99:
            break
        else:
            print('Getting selected article...')
            d.get(t_10[int(selection)]['link'])
            print_article()

    # exit chromedriver
    d.quit()
