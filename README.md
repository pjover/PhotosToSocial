# PhotosToBuffer

PhotosToBuffer is a tool to publish post with photos into [Buffer](https://buffer.com). The goal is to be able to post at least a photo every day without effort.

The workflow is like this:

Export the photos from lightroom or your favourite program. Photo's metadata will be used for:
   - `Title` will be added to the post text.
   - `Caption` will be added to the post text.
   - `IPTC Subject Code` will be used to group photos in the same post, all photos will be grouped by `Event` content (if it is not empty); you can put there any text you want, is only used for grouping.
   - `Keywords` starting with `#` will be added to the post.
1. Processor
   - Read all JPEG photos from configured `inputDirectory` directory.
   - Read already processed photos from storage.
   - Identify the new photo files to be processed.
   - Extract metadata into `Image` object:
     - `caption` with `Caption` tag content
     - `additional_info` with `Additional Info` tag content
     - `event` with `Event` tag content
     - `keywords[]` with all `Keywords` starting with `#`
   - Remove all metadata from the photos except:
       - `Caption`
       - `Additional Info`
       - `Event`
       - `Keywords` starting with `#`
       - `Creator`
       - `Copyright`
       - `Copyright Status`
       - `Rights Usage Terms`
       - `Copyright Info URL`
       - `E.Mail`
   - Update the photo files with updated metadata into configured `outputDirectory` directory.
   - Store the metadata (`caption`, `additional_info`, `event`, `keywords[]`) and when the file was processed into storage (`processed=now()`, `scheduled=null`).
2. Scheduler
   - Read not scheduled photos (`scheduled=null`) from storage.
   - Identify images to be published.
   - Group photos by `event` field
   - Set publishing date.
   - Schedule a batch for every `event` into every configured Buffer channel `channels[]`, keeping the max scheduled posts under the free tier limit (10 per channel).
   - Store the scheduled photos (`scheduled=now()`) info in storage.

We will store an read from database to be able to keep track of the state of every photo, and run the entire process even if there are no new photos, but som of them can be scheduled and published. The database is implemented with SQLite.

