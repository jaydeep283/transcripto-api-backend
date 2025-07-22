# Audio Transcription API Documentation

This document provides an overview of all API routes, including their methods, endpoints, expected request bodies, and responses.

---

## Auth Endpoints

### 1. **Register**

-   **POST** `/api/v1/auth/register`
-   **Request Body:**
    ```
    {
        "username": "string",
        "email": "user@example.com",
        "password": "string"
    }
    ```
-   **Response:**
    ```
    {
        "id": 0,
        "username": "string",
        "email": "string",
        "is_active": true,
        "is_superuser": true
    }
    ```

### 2. **Login**

-   **POST** `/api/v1/auth/login`
-   **Request Body:**
    ```
    username & password in form
    ```
-   **Response:**
    ```
    {
        "access_token": "string",
        "token_type": "string"
    }
    ```

---

## Transcriptions Endpoints

### 3. **Upload Transcription**

-   **POST** `/api/v1/transcriptions/upload`
-   **Request Body:**
    -   Audio file media (multipart file upload)
-   **Response:**
    ```
    {
        "job_id": 0,
        "message": "string",
        "status": "pending"
    }
    ```

### 4. **Get Transcription (by Job ID)**

-   **GET** `/api/v1/transcriptions/{job_id}`
-   **Request:**
    -   Job Id as path parameter
-   **Response:**
    ```
    {
        "id": 0,
        "filename": "string",
        "status": "pending",
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z",
        "started_at": "2019-08-24T14:15:22Z",
        "completed_at": "2019-08-24T14:15:22Z",
        "transcript_text": "string",
        "confidence_score": 0,
        "processing_time": 0,
        "speaker_diarization_results": {},
        "sentiment_analysis_results": {},
        "summary": "string",
        "error_message": "string"
    }
    ```

### 5. **Delete Transcription**

-   **DELETE** `/api/v1/transcriptions/{job_id}`
-   **Request:**
    -   Job Id as path parameter
-   **Response:**
    -   200: `null`
    -   422:
        ```
        {
            "detail": [
                {
                    "loc": ["string"],
                    "msg": "string",
                    "type": "string"
                }
            ]
        }
        ```

### 6. **List All Transcriptions**

-   **GET** `/api/v1/transcriptions/`
-   **Request:** `null`
-   **Response:**
    ```
    [
        {
            "id": 0,
            "filename": "string",
            "status": "pending",
            "created_at": "2019-08-24T14:15:22Z",
            "updated_at": "2019-08-24T14:15:22Z",
            "started_at": "2019-08-24T14:15:22Z",
            "completed_at": "2019-08-24T14:15:22Z",
            "transcript_text": "string",
            "confidence_score": 0,
            "processing_time": 0,
            "speaker_diarization_results": {},
            "sentiment_analysis_results": {},
            "summary": "string",
            "error_message": "string"
        }
    ]
    ```

---

## User Endpoints

### 7. **Get Current User**

-   **GET** `/api/v1/users/me`
-   **Request:** `null`
-   **Response:**
    ```
    {
        "id": 0,
        "username": "string",
        "email": "string",
        "is_active": true,
        "is_superuser": true
    }
    ```

### 8. **Update Current User**

-   **PUT** `/api/v1/users/me`
-   **Request Body:**
    ```
    {
        "username": "string",
        "email": "user@example.com",
        "password": "string",
        "is_active": true,
        "is_superuser": true
    }
    ```
-   **Response:**
    ```
    {
        "id": 0,
        "username": "string",
        "email": "string",
        "is_active": true,
        "is_superuser": true
    }
    ```

### 9. **List Users**

-   **GET** `/api/v1/users/`
-   **Request:** `null`
-   **Response:**
    ```
    [
        {
            "id": 0,
            "username": "string",
            "email": "string",
            "is_active": true,
            "is_superuser": true,
            "created_at": "2019-08-24T14:15:22Z",
            "updated_at": "2019-08-24T14:15:22Z"
        }
    ]
    ```

### 10. **Get User by ID**

-   **GET** `/api/v1/users/{user_id}`
-   **Request:** `null`
-   **Response:**
    ```
    {
        "id": 0,
        "username": "string",
        "email": "string",
        "is_active": true,
        "is_superuser": true,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
    }
    ```

### 11. **Update User by ID**

-   **PUT** `/api/v1/users/{user_id}`
-   **Request Body:**
    ```
    {
        "username": "string",
        "email": "user@example.com",
        "password": "string",
        "is_active": true,
        "is_superuser": true
    }
    ```
-   **Response:**
    ```
    {
        "id": 0,
        "username": "string",
        "email": "string",
        "is_active": true,
        "is_superuser": true,
        "created_at": "2019-08-24T14:15:22Z",
        "updated_at": "2019-08-24T14:15:22Z"
    }
    ```

### 12. **Delete User**

-   **DELETE** `/api/v1/users/{user_id}`
-   **Request:**
    -   User Id as path parameter
-   **Response:** `null` (200)

### 13. **Activate User**

-   **POST** `/api/v1/users/{user_id}/activate`
-   **Request:**
    -   User Id as path parameter
-   **Response:** `null` (200)

### 14. **Deactivate User**

-   **POST** `/api/v1/users/{user_id}/deactivate`
-   **Request:**
    -   User Id as path parameter
-   **Response:** `null` (200)

### 15. **Make User Superuser**

-   **POST** `/api/v1/users/{user_id}/make-superuser`
-   **Request:**
    -   User Id as path parameter
-   **Response:** `null` (200)

### 16. **Remove Superuser**

-   **DELETE** `/api/v1/users/{user_id}/remove-superuser`
-   **Request:**
    -   User Id as path parameter
-   **Response:** `null`

---

## Utility Endpoints

### 17. **API Root**

-   **GET** `/`
-   **Response:**
    ```
    {
        "message": "Audio Transcription API",
        "version": "1.0.0"
    }
    ```

### 18. **Health Check**

-   **GET** `/health`
-   **Response:**
    ```
    {
        "status": "healthy"
    }
    ```
