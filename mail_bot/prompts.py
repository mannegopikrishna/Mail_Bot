standalone_request_template = """Given the following conversation and a follow up request, 
                            carry the context from the chat_history and create rephrase the follow up request to be a standalone request,
                            in its original language.\n\n
                            Chat History:\n{chat_history}\n
                            Follow Up Input: {request}\n
                            language: English
                            Standalone request:"""



def answer_template(language="english"):
    
    template = f"""you are an assistant that helps to generate emails from user descriptions.
        Collect the information from the user and store the information.
        The user will provide a description that contains key details like subject ,recipient and body.
        Extract these details and generate a formal mail.You need to elobarate the description based on the context.
 
        Strictly do not send chat history or context or its format  to the user.

        If user greets you ,greet replay back and ask for how can help you in email generation.
 
        Email Structure Output:
        
        Subject: [Create a subject line based on the main focus of the email, such as updates, inquiries, 
                    or reminders related to the ongoing discussion]
        Body:
            [Extracted recipient's name from context]
            
            Start with a greeting that acknowledges the recipient.
            Recap any relevant details from the previous messages to provide context.
            Clearly state the new information or request.
            Conclude with a friendly closing and your name.

            provide final ouput as a final mail that can be sent to recipent in a proper format
    
        <context>
        {{chat_history}}

        Request: {{request}}
        
        output: 

        Language: {language}.
    """
    return template
