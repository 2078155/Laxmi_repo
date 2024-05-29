def count_characters_and_words(sentence):
    # Calculate character count
    char_count = len(sentence)

    # Calculate word count
    words = sentence.split()
    word_count = len(words)

    return char_count, word_count