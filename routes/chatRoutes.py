from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from core.rag import query_index
from schemas.schemas import QuestionRequest
from core.imgExtraction import decode_image, extract_text_from_image
from utils.shared_limiter import limiter

chat = APIRouter()

@chat.get('/api', tags=['chat_main_endpoint'])
@limiter.limit("20/minute")
async def chatWelcome(request: Request):
    return JSONResponse({'message': 'Welcome to the Chat Endpoint!'})


# ImageUrl would be a base64 string (validate it!) and the query should be limited by length

@chat.post('/api')
@limiter.limit("10/minute")
async def chatQuery(data: QuestionRequest, request: Request):
    index = request.app.state.index
    query = data.question
    intelligence = False

    if data.image:
        intelligence = True
        img = decode_image(base64_img=data.image)
        ocr_text = await extract_text_from_image(image=img)
        query += "\n\n" + "Text Extracted From Question : " + ocr_text

    response = query_index(index=index, query=query, intelligence=intelligence)

    return JSONResponse(response)
