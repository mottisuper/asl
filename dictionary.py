class Dictionary:
  def __init__ (self):
    #loading dictionary from file
    self.word_frequency = load_word_frequency("frequency_dictionary_en_82_765.txt")

  # function to get list of suggestion by prefix of word
  def suggest_words(self, current_word, max_suggestions=4):
      suggestions = {word: freq for word, freq in self.word_frequency.items() if word.startswith(current_word.lower()) and len(word) != len(current_word)}
      sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
      return [word for word, _ in sorted_suggestions[:max_suggestions]]

# function for loading dictionary from file and return as dictionary of python (pairs of words and frequencies)
def load_word_frequency(file_path):
  word_frequency = {}
  with open(file_path, 'r', encoding='utf-8') as f:
      for line in f:
          parts = line.split()
          if len(parts) == 2:
              word, frequency = parts
              word_frequency[word] = int(frequency)
  return word_frequency