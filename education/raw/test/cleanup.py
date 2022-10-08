def main():
    import os
    years = [2016, 2017, 2018, 2019]
    for year in years:
        filename = f'test{year}.txt'
        file = open(filename, 'r', encoding='utf8')
        text = file.read()
        file.close()
        text = text.replace('"', '')
        with open(f'test{year}.csv', 'w', encoding='utf8') as f:
            f.write(text)
        os.remove(filename)

if __name__ == '__main__':
    main()