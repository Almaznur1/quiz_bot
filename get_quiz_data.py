def get_quiz_data(path):
    with open(path, 'r', encoding='koi8-r') as file:
        quiz_data = {}
        text_blocks = file.read().split('\n\n')

    for block in text_blocks:
        if block.startswith('Вопрос '):
            question = ' '.join(block.split('\n')[1:])
        elif block.startswith('Ответ:'):
            answer = block.split('\n')[1]
            quiz_data[question] = answer

    return quiz_data
