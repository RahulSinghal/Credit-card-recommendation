# Corrected System Architecture

## Actual Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│   Extractor     │───▶│     Router      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                                 │                                 │
                       ▼                                 ▼                                 ▼
              ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
              │ Travel Manager  │              │ Business Manager│              │ Student Manager │
              └─────────────────┘              └─────────────────┘              └─────────────────┘
                       │                                 │                                 │
                       ▼                                 ▼                                 ▼
              ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
              │ Cashback Manager│              │ General Manager │              │     Summary     │
              └─────────────────┘              └─────────────────┘              └─────────────────┘
                       │                                 │                                 
                       └─────────────────────────────────┘                                 
                                                         │                                 
                                                         ▼                                 
                                              ┌─────────────────┐                         
                                              │     Summary     │                         
                                              └─────────────────┘                         
                                                                                          
                                                                                          
                                              ┌─────────────────┐                         
                                              │ Online Search   │◀────────────────────────
                                              │   (Fallback)    │                         
                                              └─────────────────┘                         
                                                         │                                 
                                                         ▼                                 
                                              ┌─────────────────┐                         
                                              │     Summary     │                         
                                              └─────────────────┘                         
```

## Key Points:

1. **Router** can route to:
   - **Travel Manager**, **Business Manager**, **Student Manager** → **Summary**
   - **Online Search** (as fallback when no cards available in database) → **Summary**

2. **Card Managers** connect directly to **Summary**

3. **Online Search** is used as fallback and also connects to **Summary**

This is the correct architecture based on your clarification.
