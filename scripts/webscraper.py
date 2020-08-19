import argparse
import bs4
import requests
import pandas as pd
import urllib

from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--outdir', default='blogs',
                        help='Directory to save blog text')
    parser.add_argument('-d', '--datafile', default='blog_metadata.csv',
                        help='File to save the blog metadata')
    return parser.parse_args()


def get_soup(url):
    return bs4.BeautifulSoup(requests.get(url).content, 'lxml')


def write_text(post_date, post_title, post_text, outdir):
    outpath = Path(outdir).joinpath(
        str(post_date), post_title).with_suffix('.txt')
    if not outpath.parent.exists():
        outpath.parent.mkdir(parents=True)
    print(f'Writing to {outpath}')
    outpath.write_text(post_text)
    return outpath


def main():
    args = parse_args()
    url = 'http://jonathannelson.io'
    soup = get_soup(url)
    data = []
    for link in soup.find_all('li', class_="nav-item"):
        page_url = urllib.parse.urljoin(url, link.find('a')['href'])
        page_soup = get_soup(page_url)
        for post in page_soup.find_all(class_="post-preview"):
            post_title = post.find(class_="post-title").text
            post_date = pd.to_datetime(
                post.find(class_="post-meta").text.split(' · ')[0]).date()
            post_url = urllib.parse.urljoin(url, post.find('a')['href'])
            post_soup = get_soup(post_url)
            post_text = post_soup.find_all(
                'div', class_="container")[2].get_text('\n')
            outpath = write_text(post_date, post_title, post_text, args.outdir)
            data.append((
                post_date, post_title, post_url, outpath
            ))
    df = pd.DataFrame(data, columns=['date', 'title', 'url', 'filepath'])
    df.to_csv(args.datafile)


if __name__ == '__main__':
    main()
