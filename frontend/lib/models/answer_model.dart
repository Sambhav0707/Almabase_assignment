class AnswerModel {
  final int answerId;
  final int questionNumber;
  final String question;
  final String generatedAnswer;
  final String? editedAnswer;
  final List<dynamic> citations;

  AnswerModel({
    required this.answerId,
    required this.questionNumber,
    required this.question,
    required this.generatedAnswer,
    this.editedAnswer,
    required this.citations,
  });

  factory AnswerModel.fromJson(Map<String, dynamic> json) {
    return AnswerModel(
      answerId: json['answer_id'],
      questionNumber: json['question_number'],
      question: json['question'],
      generatedAnswer: json['generated_answer'],
      editedAnswer: json['edited_answer'],
      citations: json['citations'] ?? [],
    );
  }
}
