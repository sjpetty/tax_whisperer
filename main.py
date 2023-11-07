from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.agents import Tool
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.chat_models import ChatOpenAI
import json
from langchain.schema.messages import SystemMessage



def get_tax_account(email):
    with open('tax_account.json') as f:
        accounts = json.load(f)
        print(accounts)
        for account in accounts:
            if account["email"] == email:
                # Print or return the citizen's information
                print(account)
                return account
        print("can not find account - failed")
        return False


# enip email NI num PIN
def authenticate_citizen(enip):
    if enip.count(',') == 2:
        print(enip)
        with open('citizen.json') as f:
            citizens = json.load(f)
            print(citizens)
            # Define the email address to search for
            # email = "aisha.khan@example.com"
            input_list = enip.split(',')
            email, national_insurance_number, pin = input_list
            # Iterate over the dictionary and check if the email matches
            for citizen in citizens:
                if citizen["email"] == email:
                    # Print or return the citizen's information
                    print(citizen)
                    # yes I know its very poor to have a function returning mixed types
                    # but it works
                    return citizen
            print(f"can not find customer with email: {email} - failed")
            return False

    else:
        # Authentication failed
        print(f"bad argument passed: {enip}")
        return False


embedding_function = OpenAIEmbeddings()
alcohol_db = FAISS.load_local("faiss_index_alcoholic-ingredients-relief", embedding_function)
biofuel_db = FAISS.load_local("faiss_index_biofuels-and-fuel-substitutes-assurance", embedding_function)
capital_allowances_db = FAISS.load_local("faiss_index_capital-allowances-manual", embedding_function)
inheritance_tax_db = FAISS.load_local("faiss_index_inheritance-tax-manual", embedding_function)
paye_db = FAISS.load_local("faiss_index_paye-manual", embedding_function)
alcohol_retriever = alcohol_db.as_retriever()
biofuel_retriever = biofuel_db.as_retriever()
capital_allowances_retriever = capital_allowances_db.as_retriever()
inheritance_tax_retriever = inheritance_tax_db.as_retriever()
paye_retriever = paye_db.as_retriever()

auth_tool = Tool(
    name="authenticate_citizen",
    func=authenticate_citizen,
    description=""" To authenticate a human before accessing their data.
    You MUST FIRST obtain 3 facts from the human. NEVER NEVER EVER make these facts up!!! 
    You MUST obtain them from the human. To collect the 3 facts, exchange 3 messages as follows:
    (Message 1): Let me authenticate you. Please provide your email address
    (Message 2): Please provide your National Insurance Number
    (Message 3): Finally, please provide your PIN
    Call the authenticate_citizen function with a single string composed these three facts separated by 
    commas ",".
    The function returns a dictionary object representing the citizen if the customer has been successfully
    authenticated and False if not.
    Make sure you authenticate the human successfully before responding to requests for personal data. 
    You MUST MUST respond to the human to let them know if they have been successfully authenticated
    """
)
alcohol_tool = create_retriever_tool(
    alcohol_retriever,
    "search_alcohol_ingredients_relief",
    """Searches and returns documents relating to control, policy and legal aspects of the 
    Alcoholic Ingredients Relief (AIR) scheme, whereby the duty paid on alcohol used in the 
    production or manufacture of eligible articles (foodstuffs and soft drinks), can be recovered 
    by an eligible person.
    You should ALWAYS include your references in your response to the human"""
)
account_tool = Tool(
    name="get_tax_account",
    func=get_tax_account,
    description=""" useful when access is needed to a human's tax account
    YOU MUST ALWAYS authenticate a customer before accessing their tax account
    Pass the human's email address to the function and if the Tax Account can be found it will be returned.
    If the Tax Account cannot be found False will be returned"""
)
biofuel_tool = create_retriever_tool(
    biofuel_retriever,
    "search_biofuels",
    """Searches and returns documents relating to guidance on the assurance of biofuels 
    and fuel substitutes.
    You should ALWAYS include your references in your response to the human"""
)
inheritance_tax_tool = create_retriever_tool(
    inheritance_tax_retriever,
    "search_inheritance_tax",
    """Searches and returns documents providing guidance related to Inheritance Tax
    You should ALWAYS include your references in your response to the human"""
)
capital_allowances_tool = create_retriever_tool(
    capital_allowances_retriever,
    "search_capital_allowances",
    """Searches and returns documents relating to the definition  of capital allowances, 
    how allowances are made and how to claim.
    You should ALWAYS include your references in your response to the human
    """
)
paye_tool = create_retriever_tool(
    paye_retriever,
    "search_paye",
    """Searches and returns documents relating to Pay As You Earn (PAYE) taxation.
    It contains information on a wide range of topics related to PAYE.
    "Searches and returns documents related to PAYE taxation. It contains information on tax codes, 
    student loan deductions, National Insurance contributions, and how to handle special types of payment such 
    as bonuses, tips, and expenses. It also provides guidance on calculating employment income, 
    handling different types of employment income, expenses, and benefits, and the different types of 
    employment status and how they affect PAYE. It also explains how to handle employment intermediaries such 
    as agencies and umbrella companies, and how to calculate business income for self-assessment tax returns."
    You should ALWAYS include your references in your response to the human
    """
)
tools = [alcohol_tool, biofuel_tool, inheritance_tax_tool, capital_allowances_tool,
         auth_tool, account_tool, paye_tool]


new_system_message = SystemMessage(
    content=(
        "You are an assistant that always follows the steps to use "
        "the authenticator tool. "
        "Do your best to answer the questions. "
        "Feel free to use any tools available to look up "
        "relevant information, particularly more tax related questions. "
        "There are steps you must complete BEFORE using the authentication tool"
        "BEFORE using the authentication tool you must collect three facts FROM THE HUMAN: "
        "email, national insurance number and PIN"
        "All three facts MUST be elicited from human individually via three separate chat exchanges"
        ", you MUST NEVER make up these facts or use "
        "example data instead of data obtained from the human"
        "These are passed to the authentication tool in a single comma ',' separated string. "
        "The authentication tool cannot be used in any other way, you must pass these"
        "three facts in a comma (') separated string"
        "You must never make up a human's email, national insurance number or PIN, always get"
        "these by chatting with the human"

    )
)
# gpt_model='gpt-4'
gpt_model = "gpt-3.5-turbo"
llm = ChatOpenAI(temperature=0, model=gpt_model)

agent_executor = create_conversational_retrieval_agent(llm, tools)
agent_executor.agent.prompt.messages[0] = new_system_message

print(type(agent_executor))
if __name__ == '__main__':
    from tkinter import *
    from tkinter.ttk import *

    root = Tk()
    root.title("TaxWhisperer")
    # Create the chatbot's text area
    text_area = Text(root, bg="white", width=200, height=40)
    text_area.pack()

    # Create the user's input field
    input_field = Entry(root, width=200)
    input_field.pack()

    # Create the send button
    send_button = Button(root, text="Send", command=lambda: send_message())
    send_button.pack()


    def send_message():
        # Get the user's input
        user_input = input_field.get()

        # Clear the input field
        input_field.delete(0, END)

        # Generate a response from the chatbot
        response = agent_executor({"input": user_input})['output']

        # Display the response in the chatbot's text area
        text_area.insert(END, f"User: {user_input}\n")
        text_area.insert(END, f"Chatbot: {response}\n")


    root.mainloop()
