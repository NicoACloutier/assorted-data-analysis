def main():
    import os
    
    #convert raw txt files to csv
    
    num_files = 6
    lowest = 16
    basic = 'filesenr'
    for i in range(num_files):
        with open(f'{basic}{lowest+i}.txt', 'r', encoding='utf8') as file:
            text = file.read()
            text = text.replace(',', '')
            text = text.replace('	', ',')
            with open(f'{basic}{lowest+i}.csv', 'w', encoding='utf8') as f:
                f.write(text)
        os.remove(f'{basic}{lowest+i}.txt')

if __name__ == '__main__':
    main()