def load_docs(topic):
    from bs4 import BeautifulSoup
    from langchain.document_loaders import RecursiveUrlLoader

    # define the extractor function
    def extractor(html):
        # use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(html, "html.parser")

        # find all <article> tags
        tags = soup.find_all("article")

        # join the text of all tags with a newline
        text = "\n".join(tag.get_text() for tag in tags)
        return text

    # create a RecursiveUrlLoader instance with the extractor
    url = f"https://www.gov.uk/hmrc-internal-manuals/{topic}"  # the webpage you want to crawl
    loader = RecursiveUrlLoader(url=url, max_depth=10, extractor=extractor)

    # load and print the documents
    print(f"Starting to load documents from: {url}")
    docs = loader.load()
    print(f"The number of docs for {topic} is: ")
    print(len(docs))

    # split docs
    from langchain.text_splitter import CharacterTextSplitter
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    print(f"Splitting documents for topic: {topic}")
    split_docs = text_splitter.split_documents(docs)

    # embed docs
    # tried Chroma, I could not get it to persist. FAISS worked first time.
    from langchain.vectorstores import FAISS
    from langchain.embeddings import OpenAIEmbeddings

    embedding_function = OpenAIEmbeddings()
    print(f"Embedding documents for: {topic}")
    db = FAISS.from_documents(split_docs, embedding_function)
    db.save_local(f"faiss_index_{topic}")
    db_new_connection = FAISS.load_local(f"faiss_index_{topic}", embedding_function)
    # check embedding worked
    query = "what is alcohol ingredient relief"
    db_results = db.similarity_search(query)
    print("similarity search in db")
    print(db_results[0].metadata['source'])
    # check persisted db is working
    new_db_results = db_new_connection.similarity_search(query)
    print("similarity search in persisted db")
    print(new_db_results[0].metadata['source'])


if __name__ != '__main__':
    pass
else:
    load_docs("alcoholic-ingredients-relief")
    # load_docs("biofuels-and-fuel-substitutes-assurance")
    # load_docs("capital-allowances-manual")
    # load_docs("inheritance-tax-manual")
    #load_docs("paye-manual")
